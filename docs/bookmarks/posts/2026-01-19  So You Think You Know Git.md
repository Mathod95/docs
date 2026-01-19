---
title: "So You Think You Know Git"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@lordmoma/so-you-think-you-know-git-673f9c4b0792"
author:
  - "[[David Lee]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Mastodon](https://me.dm/@lordmoma)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*W1LPtxxrJ0J1cq_Pv_OWbQ.png)

I’ve been working with Git for a while and for a long time I did not know I could take the Git use to the next level. I thought Git is merely add, commit push and pull. And I could survive most of the time with these simple command, until …

Here is the list of my git tools that have taken my work skill to the next level, and I hope it will help you too.

Set below for your.gitconfig file:

```c
[alias]
 graph = log --oneline --graph --decorate
 ls = log --pretty=format:"%C(yellow)%h%Cred%d\\ %Creset%s%Cblue\\ [%cn]" --decorate
 ll = log --pretty=format:"%C(yellow)%h%Cred%d\\ %Creset%s%Cblue\\ [%cn]" --decorate --numstat
 lds = log --pretty=format:"%C(yellow)%h\\ %ad%Cred%d\\ %Creset%s%Cblue\\ [%cn]" --decorate --date=short
 conflicts = diff --name-only --diff-filter=U
 local-branches = !git branch -vv | cut -c 3- | awk '$3 !~/\\[/ { print $1 }'
 recent-branches = !git branch --sort=-committerdate | head
 authors = !git log --format='%aN <%aE>' | grep -v 'users.noreply.github.com' | sort -u --ignore-case
 search = "!f() { git rev-list --all | xargs git grep -F \"$1\"; }; f"
 dl = "!git ll -1" # Show modified files in last commit:latest commit
 dlc = diff --cached HEAD^ # Show modified files in last commit:latest commit
 dr  = "!f() { git diff "$1"^.."$1"; }; f" # git dr <commit-id> 
        lc  = "!f() { git ll "$1"^.."$1"; }; f" # git lc <commit-id> # show modified files in <commit-id>
        f = "!git ls-files | grep -i" # git f <filename> # search <filename> in all files
 bb = !/Users/davidlee/.dotfiles/scripts/better-branch.sh
 fza = "!git ls-files -m -o --exclude-standard | fzf -m --print0 | xargs -0 git add"
 alias = ! git config --get-regexp ^alias\\. | sed -e 's/^alias\\.\\([^ ]*\\) \\(.*\\)$/\\x1b[36m\\1\\x1b[0m=\\x1b[35m\\2\\x1b[0m/'
[core]
 pager = diff-so-fancy | less --tabs=4 -RF
[interactive]
 diffFilter = diff-so-fancy --patch
```

## How powerful they are?

git graph:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rmaNf0DykV1PQQ7xXbZ5hw.png)

git ls:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*blRJ6XB4aiCMa_t8Q34Uvg.png)

git ll

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*w-QX2Qz0ZaOfeu_u44a--w.png)

git lds

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5pCQhraaarf43AtV47dxeA.png)

git dr <commit id> (below is git dr 3035221)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*gjP2RHBHwajTMGD3Ce2JVQ.png)

You can try to experiment the rest after you specified above file in your own.gitconfig file.

Let’s stay inside the terminal!

A Rustacean/Gopher, and serial entrepreneur 🇨🇦 based in Toronto. Love travel, writing and bird watching! currently building: [www.crimewatches.com](http://www.crimewatches.com/)

## More from David Lee

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--673f9c4b0792---------------------------------------)