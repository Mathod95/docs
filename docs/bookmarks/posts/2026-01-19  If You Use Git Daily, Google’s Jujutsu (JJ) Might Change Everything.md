---
title: "If You Use Git Daily, Google’s Jujutsu (JJ) Might Change Everything"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@PowerUpSkills/if-you-use-git-daily-googles-jujutsu-jj-might-change-everything-0daf3d21087e"
author:
  - "[[Jannis]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@PowerUpSkills)

What if I told you there’s a version control system developed at Google that removes most of Git’s pain points while remaining fully compatible with your existing Git repositories?

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*Wilvn-MQ7nUM0UmCtMP7ig.png)

If you’re like most developers, you’ve probably mastered a handful of Git commands that get you through your daily workflow. `git add .`, `git commit -m`, `git push`, maybe some rebasing when things get messy.

==You've learned to live with merge conflicts, u== nderstand the staging area, and have probably typed `git stash` more times than you'd like to admit.

### Ladies and Gentlemen may I introduce: JJ

> **Jujutsu** (command: `jj`), might just be the tool that makes you forget about Git's quirks forever.

## What Is JJ (Jujutsu)?

It’s a different approach to version control, created by Martin von Zweigbergk, a software engineer at Google who works on source control systems.

The project started as a hobby in 2019 but has since become a full-time project at Google, designed to potentially replace their internal version control infrastructure.

**Jujutsu uses Git repositories as its storage layer**.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*04YuJJBWRVmYeYbWjOliMQ.png)

## The Biggest Differences When Compared To Git

## No More Staging Area Confusion

In Git, you have three states to juggle:

- Working directory
- ==Staging area (index)==
- Committed changes

In JJ, there’s just one concept: **everything is a commit**.

==Your working copy is literally a commit that gets automatically updated as you make changes.==

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*L470JrpcsuFIB1Q0RzJ7Kw.png)

```c
# Git workflow
$ echo "console.log('hello');" > app.js
$ git add app.js
$ git commit -m "Add hello world"
```
```c
# JJ workflow  
$ echo "console.log('hello');" > app.js
$ jj describe -m "Add hello world"
# That's it. No staging required.
```

## Stashing Becomes Obsolete

Ever been in the middle of something and needed to quickly check out another branch? In Git, you either commit incomplete work or stash it. ==In JJ, your work is already committed (automatically),== so you can just switch to any other commit without losing anything.

```c
# Git: "oh crap, I need to check something else"
$ git stash push -m "work in progress"
$ git checkout other-branch
# do stuff...
$ git checkout my-branch  
$ git stash pop
```
```c
# JJ: "no problem"
$ jj edit other-commit-id
# do stuff...
$ jj edit @  # back to where you were
```

## History Editing That Is Less Stressful

Want to fix a typo in a commit from 3 commits ago? In Git, you’re looking at interactive rebasing, potential conflicts, and a lot of stress. ==In JJ, you just edit that commit directly, and all descendant commits are automatically rebased==.

```c
# Want to fix commit abc123 in JJ?
$ jj edit abc123
$ # make your changes
$ jj describe -m "Updated commit message"
$ jj edit @  # back to latest
# All descendant commits automatically rebased!
```

## Conflicts as First-Class Citizens

==JJ treats conflicts not as textual diffs that need immediate resolution, but as first-class objects in the version control model. This means conflict resolutions can be automatically propagated through descendant commits — no more fixing the same conflict multiple times during complex rebases.==

## How A Typical JJ Workflow looks

### Starting a New Feature

```c
# Clone any Git repo and start using JJ
$ jj git clone --colocate git@github.com:yourname/project.git
$ cd project
```
```c
# Start new work (creates a new empty commit)
$ jj new -m "Add user authentication"
# Work on files - they're automatically tracked
$ vim auth.js
$ vim routes.js
# Check your progress anytime
$ jj diff
$ jj status
# When ready for next piece of work
$ jj new -m "Add login validation"
```

## Working with Branches

==JJ uses “anonymous branches” by default. You don’t need to name every small change. But when you need to push to GitHub, you use “bookmarks”:==

```c
# Create a bookmark for GitHub  
$ jj bookmark create feature-auth
```
```c
# Push to your Git remote
$ jj git push
# The remote sees a normal Git branch named "feature-auth"
```

## The Power of Change IDs

Unlike Git commits that get new hashes when you amend them, JJ uses stable “change IDs” that persist even as you modify the commit:

```c
$ jj log
@ abcdefgh you@email.com 2024-06-20 12:34:56 9a2b3c4d
│ Add authentication logic
○ qrstuvwx you@email.com 2024-06-20 11:30:22 5e6f7g8h  
│ Initial setup
```

The letters on the left (`abcdefgh`) are change IDs. They stay the same even if you edit the commit. The hex on the right (`9a2b3c4d`) are Git commit hashes that change with edits.

## Installation and Getting Started

Getting JJ up and running is straightforward:

```c
# macOS
$ brew install jj
```
```c
# Linux (various package managers)
$ sudo pacman -S jujutsu  # Arch
$ sudo zypper install jujutsu  # openSUSE
# Or download precompiled binaries from GitHub
```

To start using it with an existing Git repo:

```c
$ cd your-existing-git-repo
$ jj git init --colocate
```

The `--colocate` flag means JJ and Git will work side by side. You can still use Git commands when needed, and JJ will sync with any changes.

## Are There Drawbacks?

JJ isn’t perfect. You have to deal with limitations:

==**Performance**====: Some operations can be slower than Git on very large repositories, though the team is actively working on improvements.==

**Tooling**: There’s less ecosystem support compared to Git. Your favorite Git GUI or IDE integration might not work with JJ (yet).

**Learning Curve**: ==While simpler conceptually, you’ll need to unlearn some Git habits and learn new commands.==

**Temporary Files**: Since JJ snapshots everything automatically, you’ll need to be more careful about `.gitignore` files to avoid tracking build artifacts.

## If you don’t rely heavily on specific Git tooling or GUIs, here is how to get started:

1. **Install JJ** using the methods above
2. **Try it with a test repo** first: `jj git clone --colocate [https://github.com/jj-vcs/jj.git](https://github.com/jj-vcs/jj.git)`
3. **Read the basics**: Run `jj help` and check out [Steve Klabnik's tutorial](https://steveklabnik.github.io/jujutsu-tutorial/)
4. **Start small**: Use it for a side project before considering it for work projects
5. **Remember**: You can always fall back to Git commands in the same repo

As one developer put it: *“If using the Git CLI is bumping into a wall with your shoulder at full speed, using jj is like getting a gentle and pleasant back massage.”*

Ready to give your daily version control workflow that massage?

**If you found this article helpful, a few claps 👏, a highlight 🖍️, or a comment 💬 really helps.**

**If you hold that 👏 button down something magically will happen, Try it!**

Don’t forget to follow me to stay updated on my latest posts. Together, we can continue to explore fascinating topics and expand our knowledge.

*Want to dive deeper? Check out the* [*official JJ documentation*](https://jj-vcs.github.io/jj/latest/) *or* [*GitHub Discussions*](https://github.com/jj-vcs/jj/discussions)*.*

Product Owner in global telecom, lifelong tech tinkerer, and Mac user. Sharing hands-on hacks, real stories, and the tools that make work (and life) smarter.

## More from Jannis

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--0daf3d21087e---------------------------------------)