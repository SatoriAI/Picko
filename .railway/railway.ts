// Picko's Railway settings. The CLI evaluates this file; Railway never reads it during a
// deploy, so nothing here takes effect until `railway config apply` runs.
//
// It replaces the three Config as Code files (`backend.toml`, `celery.toml`,
// `frontend.toml`), which Railway stops reading on 2026-12-01. Every value below is what
// the last deployment of each service actually ran with.
import { defineRailway, github, preserve, project, service } from 'railway/iac'

// Mark 0 also runs Athlo, Slip, tURL and Portfolio from their own repositories, so this
// file is a named partial: it owns the three Picko services it declares and nothing else.
// The shared Postgres and Redis are left alone.
export const partial = 'picko'

/**
 * Variables whose values stay on Railway. A variable the file leaves out is deleted on apply,
 * so every name a service holds is listed here; set a new one in Railway and add its name.
 */
function onRailway(...names: string[]) {
  return Object.fromEntries(names.map((name) => [name, preserve()]))
}

const REGION = { 'europe-west4-drams3a': 1 }

// A service setting's `dockerfilePath` resolves against the service's root directory
// (`/backend` or `/frontend`), so `./Dockerfile` names the same file the tomls built from.
const DOCKERFILE = { buildEnvironment: 'V3', builder: 'DOCKERFILE', dockerfilePath: './Dockerfile' } as const

const RESTART = { restartPolicyType: 'ON_FAILURE', restartPolicyMaxRetries: 5 } as const

export default defineRailway(() => {
  const picko = (rootDirectory: string) =>
    github('SatoriAI/Picko', { branch: 'main', rootDirectory, checkSuites: false })

  const api = service('Picko', {
    source: picko('/backend'),
    build: DOCKERFILE,
    // `sh -c`, because a start command gets no shell and `$PORT` would arrive literally.
    start: "sh -c 'uv run --no-sync --no-dev gunicorn -k uvicorn.workers.UvicornWorker source.app:app --bind 0.0.0.0:$PORT --workers 1'",
    preDeploy: 'uv run --no-sync --no-dev alembic upgrade head',
    healthcheck: '/status',
    // Sleeps when idle: Picko's traffic does not justify an always-on container. Set by API
    // on 2026-10-27; declared here so an apply does not wake it for good.
    deploy: { ...RESTART, sleepApplication: true },
    replicas: REGION,
    networking: {
      serviceDomains: { 'picko-production.up.railway.app': { port: 8000 } },
      privateNetworkEndpoint: 'http-server',
    },
    env: onRailway('CORS_ORIGINS', 'DATABASE_URL', 'EMAIL_FROM', 'PORT', 'REDIS_URL', 'RESEND_API_KEY'),
  })

  // Never sleeps: it consumes the Redis queue, and a sleeping consumer takes no work.
  const worker = service('Picko-Worker', {
    source: picko('/backend'),
    build: DOCKERFILE,
    start: 'uv run --no-sync --no-dev celery -A source.celery_app:celery_app worker -l info',
    deploy: RESTART,
    replicas: REGION,
    networking: { privateNetworkEndpoint: 'celery-worker' },
    env: onRailway(
      'CORS_ORIGINS',
      'DATABASE_URL',
      'DEFAULT_WORKER_CONCURRENCY',
      'EMAIL_FROM',
      'REDIS_URL',
      'RESEND_API_KEY',
    ),
  })

  const ui = service('Picko-UI', {
    source: picko('/frontend'),
    build: DOCKERFILE,
    start: 'node build',
    healthcheck: '/',
    deploy: { ...RESTART, sleepApplication: true },
    replicas: REGION,
    domains: [
      { domain: 'picko.world', port: 3000 },
      { domain: 'www.picko.world', port: 3000 },
    ],
    networking: { privateNetworkEndpoint: 'frontend' },
    env: onRailway('API_BASE_URL', 'PORT', 'PUBLIC_CHRISTMAS_THEME'),
  })

  return project('Mark 0', { resources: [api, worker, ui] })
})
