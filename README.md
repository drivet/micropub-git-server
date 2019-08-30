# Micropub Listener for Git Repositories

A small Flask application which listens for micropub create requests
and commits the result in a git repository.

This server will commit plain, minimally processed JSON files,
representing micropub entries, into a configured location of your choice.

## Background

A micropub server allows users to post content on their own website by means
of an associated micropub client, and forms one part of the [IndieWeb][2]
ecosystem, a decentralized alternative to corporate social networks, based
on open standards, where users post and *control* their own content.

Micropub is based heavily on the idea of [microformats][4] - little pieces
of metadata sprinkled in an HTML document that give some clues as to what
the content is supposed to represent.  Examples of different types of
content include:

* h-entry - an authored bit of online content, like a blog post, tweet,
  comment or reply.
* h-event - a calendar event
* h-card - contact information about a person

Please consult the [wiki][3] for information on the IndieWeb and how to
join.
