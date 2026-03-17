# Concepts and philosophy

Backstage is constructed out of three parts. We separate Backstage in this way because we see three groups of contributors that work with Backstage in three different ways:

![](https://backstage-spotify-com.spotifycdn.com/_next/static/media/IMG_key_terms.72c69cd1.png)

- Core: Base functionality built by core developers in the open source project.
- App: An instance of a Backstage app that is deployed and tweaked. The app ties together core functionality with additional plugins. The app is built and maintained by app developers, usually a productivity team within a company.
- Plugins: Additional functionality to make your Backstage app useful for your company. Plugins can be specific to a company or open sourced and reusable.

## Core philosophy
!!! note "Backstage is the interface"

    One of the core philosophies is that Backstage is the interface. It's really an aggregator. You're undoubtedly going to have many infrastructure tools and you want to expose all those tools through the same interface. Backstage is not meant to reimplement them.

    CI/CD is a good example where you want to show the status of your build. But if you want to go off and troubleshoot the build, it's probably better to launch into the external system. Reimplementing the whole portal of the external system is probably not the solution to your challenges.

    Backstage is rarely the source of truth but aggregating information from other external source systems. That makes it a lot more flexible and easy to adopt. Instead of replacing everything in your infrastructure, with Backstage you add a layer on top of it, bringing together all your sources of truth together in a single interface.

!!! note "Backstage embraces autonomy"

    At Spotify, we have a strong culture of autonomy. Basically each team is able to operate on its own and make the best decisions for themselves. From the start, we knew that we couldn't have a big central platform team that dictates everything from the top-down and implements the whole platform for everyone. This is why Backstage was built upon a plugin mechanism.

    Internally at Spotify, we have a team of 4-6 people managing our internal deployment of Backstage at the core. Then, there are hundreds of plugins created and maintained by more than 100 other teams who own that domain of expertise. For example, the plugin that shows the status of current builds is provided by the team that owns the build systems; or the plugin that shows you the status of data pipelines, is owned by the data team.

    Autonomy speeds development and keeps the experts at the heart of the problem.

!!! note "Backstage demands clear ownership"

    For each piece of software at a company, we believe there should be a single team as a point of contact. They should be the owners of the metadata and be able to declare what kind of dependencies they have.

    We follow the GitOps model, which is all about putting ownership in the hands of the teams that own the software. Not trying to build a central place of ownership.