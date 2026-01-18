---
title: 10 Terminal Tricks to Supercharge Your Developer Workflow
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://observabilityguy.medium.com/10-terminal-tricks-to-supercharge-your-developer-workflow-9d10ce15d7ea
author:
  - "[[Observability Guy]]"
---
<!-- more -->

[Sitemap](https://observabilityguy.medium.com/sitemap/sitemap.xml)

If you spend most of your day in the terminal, small improvements add up fast.  
Here are 10 simple tricks I’ve picked up over the years that genuinely made my workflow smoother. Nothing fancy, no over-engineering — just things that work.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*WLYidPBdX2zYSfe_.jpg)

## 1) Save keystrokes with quick aliases

Typing the same long commands again and again gets old. A few short aliases can save a surprising amount of time.

```c
# in your ~/.bashrc or ~/.zshrc
alias gs='git status'
alias ll='exa -la'      # nicer ls
alias ..='cd ..'
```

Even better: tools like `autojump` or `zoxide` let you jump to any folder you visit often, just by typing part of its name. It feels like magic after a day or two.

## 2) Keep sessions alive with tmux

Ever closed your terminal by accident while running a long build?  
`tmux` fixes that. It keeps your sessions alive even if you close your terminal window.

```c
tmux new -s dev      # start session
tmux attach -t dev   # reattach later
```

Inside tmux:

- `Ctrl-b c` → new window
- `Ctrl-b %` → vertical split
- `Ctrl-b d` → detach

Once you get used to it, you’ll wonder how you worked without it.

## 3) Fuzzy-find any file in seconds

Finding files in big projects is painful. Combine `ripgrep`, `fzf`, and `bat` to fly through them.

```c
rg --files --hidden --glob '!.git' \
  | fzf --preview 'bat --style=numbers --color=always --line-range :200 {}'
```
- `rg` lists all files (ignores `.gitignore`)
- `fzf` lets you fuzzy search them
- `bat` shows a nice preview

This combo alone saves me minutes every day.

## 4) Search codebases faster with ripgrep

`ripgrep` (`rg`) is like `grep` but much faster and smarter.

```c
rg 'TODO|FIXME' -n
rg --hidden --glob '!.git' 'function main' src
```

It respects `.gitignore` by default, which means fewer irrelevant results and less noise in your searches.

## 5) Use modern tools: exa, bat, delta

Some classic commands are showing their age. These drop-in replacements look better and are easier to read.

```c
exa -la --git        # like ls, but better
bat file.py           # pretty syntax-highlighted cat
git diff | delta      # clean and colorful diffs
```

They make the terminal less… gray. Small thing, big difference.

## 6) Make git feel friendlier

A few git aliases and habits can really clean up your workflow.

```c
# ~/.gitconfig
[alias]
  s = status
  lg = log --graph --oneline --decorate --all
  amend = commit --amend --no-edit
```

Helpful commands I use often:

```c
git add -p        # pick specific changes to stage
git rebase -i HEAD~5
git checkout $(git branch | fzf)
```

Once you memorize a few, `git` stops feeling scary.

## 7) Speed up SSH with multiplexing

Waiting a few seconds every time you SSH into a server adds up. Multiplexing fixes that.

```c
# ~/.ssh/config
Host *
  ControlMaster auto
  ControlPath ~/.ssh/cm-%r@%h:%p
  ControlPersist 10m
```

The first connection opens normally, and the next ones reuse the same connection instantly. It feels snappy.

## 8) Run tasks in parallel

Running tasks one by one is slow. Use `xargs` or `parallel` to run them side by side.

```c
find . -name '*.js' -print0 \
  | xargs -0 -P 8 -I {} sh -c 'eslint "{}"'
```

Just be careful not to overload your machine. A few parallel jobs can save a lot of time in builds and tests.

## 9) Load project-specific environments automatically

`direnv` is a small tool that automatically loads environment variables when you `cd` into a project.

`.envrc` file in your project:

```c
export DATABASE_URL="postgres://user:pass@localhost/db"
layout python
```

It keeps your global environment clean and avoids weird conflicts between projects.

## 10) Handy tools for quick checks

Some small tools I use all the time:

```c
htop        # live process monitor
ncdu .      # disk usage in current dir
tldr tar    # short usage examples
watch -n 2 'ps aux | wc -l'  # rerun command every 2s
```

They save you from opening a browser or clicking through GUIs just to see what’s happening.

## How all this fits together

Here’s a simple high-level view showing how these tools interact around your shell:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*C27YiVnf1Odruhcj3Ebsgw.png)

It’s just your terminal at the center, with tools hanging off it that make searching, browsing, and managing code smoother.

## Wrapping up

You don’t need to use all 10 of these at once. Pick two or three and try them this week.  
Once they stick, add a couple more.  
Before you know it, the terminal will feel less like a wall of text and more like a control center.

Software Architect | 9+ yrs in backend systems, reliability, and observability. Sharing hands-on lessons, tools, and scaling insights at observabilityguy.

## More from Observability Guy

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--9d10ce15d7ea---------------------------------------)