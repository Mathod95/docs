
## Open link in a new browser window 

* [Terraform Registry](https://registry.terraform.io/){target=_blank}
{target=_blank}

```mermaid
kanban
title Project Tasks
section To Do
  Task 1
  Task 2
section In Progress
  Task 3
section Done
  Task 4
```

```mermaid
kanban
  Todo
    [Create Documentation]
    docs[Create Blog about the new diagram]
  [In progress]
    id6[Create renderer so that it works in all cases. We also add some extra text here for testing purposes. And some more just for the extra flare.]
  id9[Ready for deploy]
    id8[Design grammar]@{ assigned: 'knsv' }
  id10[Ready for test]
    id4[Create parsing tests]@{ ticket: 2038, assigned: 'K.Sveidqvist', priority: 'High' }
    id66[last item]@{ priority: 'Very Low', assigned: 'knsv' }
  id11[Done]
    id5[define getData]
    id2[Title of diagram is more than 100 chars when user duplicates diagram with 100 char]@{ ticket: 2036, priority: 'Very High'}
    id3[Update DB function]@{ ticket: 2037, assigned: knsv, priority: 'High' }

  id12[Can't reproduce]
    id3[Weird flickering in Firefox]
```


```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
    branch feature
    checkout feature
    commit
    commit
    checkout main
    merge feature
```

```mermaid
flowchart TD
subgraph s1["Kubernetes Cluster"]

  subgraph s13["Custom Resource Definitions (CRDs)"]
    s131["abc
      abc
      abc"]
  end

  subgraph s12["Provider Controllers"]
    n8("AWS Provider")
    n7("Gitlab Provider")
    n6("Argo CD Provider")
  end

  subgraph s11["Crossplane Control Plane"]
    n5("Crossplane Controller")
    n1("Crossplane RBAC Manager")
  end

end

  subgraph s2["External Cloud Provider"]
    A ~~~ B ~~~ C
  end

s1 e1@-->|"API Calls"| s2
style s1 stroke-width:1px
e1@{ animation: fast }
```


[Attribute Lists](#pattern-matching){ data-preview }

- [Abbreviations]
- [Attribute Lists]
- [Snippets]

  [Abbreviations]: ../../../applications/crossplane/01-fundamentals/01-introduction.md#managed-resources
  [Attribute Lists]: ../../../applications/crossplane/01-fundamentals/01-introduction.md#managed-resources
  [Snippets]: ../../../applications/crossplane/01-fundamentals/01-introduction.md#managed-resources
 

 note → pour du contexte, historique, non essentiel ✅ (ton cas)
info → pour une info utile dans le flow principal
abstract → pour un résumé / introduction