import type { Guide } from './index';
import type { GuideId } from './paths';

export const en: Record<GuideId, Guide> = {
	organize: {
		seoTitle: 'How to organize Secret Santa: a step-by-step guide | Picko',
		description:
			'Everything you need to run a Secret Santa: choosing a budget and deadline, drawing names fairly, wishlists, and the exchange itself. Free, no sign-up.',
		title: 'How to organize Secret Santa, step by step',
		summary: 'Budget, deadline, the draw and the exchange: the whole plan in six steps.',
		intro: [
			'Secret Santa takes the pressure out of gift-giving: instead of buying for everyone, each person buys one good gift for one person, and nobody knows who drew whom until the exchange.',
			'It only works if the rules are clear before the names are drawn. Here is how to set it up so nobody is left out and nobody has to keep a secret they shouldn’t know.'
		],
		sections: [
			{
				heading: '1. Decide who is taking part',
				paragraphs: [
					'Start with the group: your team, your family, your friends. Ask rather than assume. Someone who is busy, short of money or away in December will be grateful for the chance to say no.',
					'Any number of people works, odd or even. Each person gives exactly one gift and receives exactly one, so you need at least two.'
				]
			},
			{
				heading: '2. Agree on a budget',
				paragraphs: [
					'A spending limit keeps things fair: nobody opens a small present next to an expensive one. Pick one number and say it out loud, rather than “around” a figure.',
					'For colleagues, something modest such as $20–30 is common. Friends and family often go higher. If anyone in the group is on a tight budget, go with the lower figure.'
				]
			},
			{
				heading: '3. Set a sign-up deadline and an exchange date',
				paragraphs: [
					'The sign-up deadline is when the draw happens. Leave at least a week between it and the exchange, so everyone has time to shop, and two weeks if gifts have to be posted.',
					'Write both dates in the invitation, so nobody has to ask.'
				]
			},
			{
				heading: '4. Draw the names',
				paragraphs: [
					'Pulling names from a hat works when everyone is in the same room, but someone often draws themselves, and the organizer usually ends up knowing more than they should.',
					'An online draw avoids both problems. In Picko you create the event with its budget and deadline, then share one sign-up link. People join with just their name, with no account or password. When the deadline passes, Picko draws everyone at once: nobody gets their own name, and each person sees only who they are buying for, on their own private page. Not even the organizer can see the full list of pairs, so the organizer can take part too.'
				]
			},
			{
				heading: '5. Ask everyone for a wishlist',
				paragraphs: [
					'A few ideas save the giver a lot of guessing. When people sign up to Picko they can add a wishlist, and the person who draws them sees it next to their name.',
					'Keep wishlists to things you would be happy to receive within the budget: a book, a hobby item, a favourite snack. Wishlists are visible to the whole group, so don’t put anything private in them.'
				]
			},
			{
				heading: '6. Plan the exchange',
				paragraphs: [
					'Decide whether gifts are opened together or taken home, and whether the givers reveal themselves. Opening one at a time and guessing the giver is half the fun.',
					'If someone can’t come, agree how their gift gets to them. For groups that won’t be in one place, see the guide to virtual Secret Santa.'
				]
			}
		]
	},
	work: {
		seoTitle: 'Secret Santa at work: how to run an office gift exchange | Picko',
		description:
			'Plan a Secret Santa for your team or office: budget, opt-in, remote colleagues and gift ideas that suit coworkers. Draw names online for free, no sign-up.',
		title: 'Secret Santa at work: an office gift exchange everyone enjoys',
		summary: 'Opt-in, a fair budget, and a draw that includes remote colleagues.',
		intro: [
			'An office Secret Santa is one of the cheapest ways to bring a team together before the holidays. It also goes wrong in predictable ways: people feel obliged to join, budgets creep up, and remote colleagues are forgotten.',
			'These steps keep it fun for everyone, including the people organizing it.'
		],
		sections: [
			{
				heading: 'Make it opt-in',
				paragraphs: [
					'Invite people, don’t enrol them. Not everyone celebrates, and not everyone wants to spend money on a colleague. With a sign-up link, joining is a choice each person makes, and nobody has to explain why they didn’t.'
				]
			},
			{
				heading: 'Keep the budget low and fixed',
				paragraphs: [
					'At work, a small fixed amount is fairest: people earn different salaries, and a modest gift is easier to choose for someone you mostly know from meetings. Set it when you create the event so everyone sees the same figure next to the name they draw.'
				]
			},
			{
				heading: 'Give people enough time',
				paragraphs: [
					'Open sign-ups about two weeks before the party and close them a week before. The draw happens when sign-ups close, so the deadline is also when everyone learns who they are buying for.',
					'Avoid deadlines that fall on a weekend or a day when half the team is away.'
				]
			},
			{
				heading: 'Include remote and hybrid colleagues',
				paragraphs: [
					'Share the sign-up link wherever the team already talks: Slack, Teams or email. Picko needs no account, so a colleague can join in a minute from any device.',
					'If some people won’t be in the office, agree how their gifts travel: delivered to their home or a parcel locker, or a digital gift such as an e-book or a subscription. The guide to virtual Secret Santa covers this in more detail.'
				]
			},
			{
				heading: 'Choose work-appropriate gifts',
				paragraphs: ['A few rules of thumb that save awkward moments:'],
				list: [
					'Avoid anything too personal, such as clothing, perfume or jokes about the person.',
					'Check before buying alcohol: not everyone drinks.',
					'Consumables and small useful things are safe: good coffee or tea, a plant, a notebook, a board game for the team room.',
					'Look at the wishlist first. People who write one usually mean it.'
				]
			},
			{
				heading: 'Let the organizer play too',
				paragraphs: [
					'In a paper draw, the organizer often knows who drew whom. Picko draws everyone at once when the deadline passes and shows each person only their own match, so the organizer can join like everyone else.'
				]
			}
		]
	},
	family: {
		seoTitle: 'Family Secret Santa: fewer gifts, better presents | Picko',
		description:
			'Run a family Secret Santa: why it beats buying for everyone, how to set the budget, involving children, and drawing names online for free with no sign-up.',
		title: 'Family Secret Santa: one good gift instead of ten',
		summary: 'Fewer gifts, less stress and a bigger budget for each present.',
		intro: [
			'In a big family, buying a present for every aunt, cousin and in-law gets expensive and leaves little time to choose any of them well.',
			'A family Secret Santa replaces all that with one thoughtful gift per person. Everyone still opens a present, and the money goes further.'
		],
		sections: [
			{
				heading: 'Why families switch to Secret Santa',
				paragraphs: ['The usual reasons people give:'],
				list: [
					'It costs less overall, so the budget for each gift can go up.',
					'Everyone shops for one person, so there is time to find something they will actually use.',
					'Fewer last-minute gift cards and duplicate presents.',
					'It works for families spread across several households and cities.'
				]
			},
			{
				heading: 'Agree the rules at a family gathering',
				paragraphs: [
					'Changing a family tradition goes better when it is agreed rather than announced. Suggest it early, for example at a November get-together, and settle the budget and the date of the exchange together.'
				]
			},
			{
				heading: 'Children',
				paragraphs: [
					'Many families keep presents for children as they are and run Secret Santa among the adults. Others let older children join, which they usually love.',
					'If a child takes part, a parent can sign them up with the child’s name and wishlist. After signing up, Picko opens the child’s private page: save that link for them, because it is where their result appears after the draw.'
				]
			},
			{
				heading: 'Couples and households',
				paragraphs: [
					'Picko draws names fully at random. Nobody draws themselves, but partners and people from the same household aren’t kept apart, so a couple may draw each other. Most families don’t mind: that couple simply exchanges one present, as they would have anyway.'
				]
			},
			{
				heading: 'When family lives far apart',
				paragraphs: [
					'Sign-up and the draw happen online, so nobody has to be in the same place. Set the deadline early enough for posted gifts to arrive, or open the presents together on a video call. The guide to virtual Secret Santa has more ideas.'
				]
			}
		]
	},
	remote: {
		seoTitle: 'Virtual Secret Santa: an online gift exchange that works | Picko',
		description:
			'How to run a virtual Secret Santa for remote teams, friends abroad or family in different cities: drawing names online, shipping, and the video-call exchange.',
		title: 'Virtual Secret Santa: how to run a gift exchange at a distance',
		summary: 'Drawing names online, getting gifts delivered, and opening them on a call.',
		intro: [
			'A virtual Secret Santa works the same way as one in person: everyone draws a name and buys one gift. What changes is the logistics, because nobody can pull a name from a hat or hand a present across the table.',
			'Most of what makes remote exchanges go wrong is timing and delivery. Plan those and the rest takes care of itself.'
		],
		sections: [
			{
				heading: 'Draw the names online',
				paragraphs: [
					'Create the event in Picko and send the sign-up link in your group chat, email or team channel. Everyone joins with just their name, from any device, without creating an account.',
					'When the deadline passes, the draw happens automatically. Each person sees who they are buying for on their own private page, or by email if they gave an address, and nobody else sees the pairs.'
				]
			},
			{
				heading: 'Start earlier than you think',
				paragraphs: [
					'Posted gifts need time, and December is the busiest month for couriers. Close sign-ups at least two to three weeks before the exchange, and longer if anyone lives in another country.'
				]
			},
			{
				heading: 'Decide how addresses are shared',
				paragraphs: [
					'Givers need a delivery address, and wishlists are visible to the whole group, so a wishlist is not the place for a home address. Agree on a way before the draw: in a close group of friends a shared address list is fine. Among colleagues, delivery to the office, a parcel locker, or a digital gift are often better.'
				]
			},
			{
				heading: 'Gifts that travel well',
				paragraphs: ['Ideas that suit an exchange at a distance:'],
				list: [
					'Digital gifts: e-books, audiobooks, a subscription, a gift card for a favourite shop.',
					'Something ordered straight from an online shop to the recipient.',
					'Small, light items that are cheap to post: books, games, specialty coffee or tea.',
					'An experience the recipient can book near them.'
				]
			},
			{
				heading: 'Open them together on a video call',
				paragraphs: [
					'Pick a time that works across time zones and open the gifts one by one on camera. Asking each person to guess their Secret Santa before the reveal keeps it lively.',
					'Ask everyone to keep their gift wrapped until the call, so the reveal still happens together.'
				]
			}
		]
	}
};
