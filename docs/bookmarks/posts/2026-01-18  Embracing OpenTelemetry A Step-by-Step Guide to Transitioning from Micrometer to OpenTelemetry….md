---
title: "Embracing OpenTelemetry: A Step-by-Step Guide to Transitioning from Micrometer to OpenTelemetry…"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@jojoooo/embracing-opentelemetry-a-step-by-step-guide-to-transitioning-from-micrometer-to-opentelemetry-cdb9f02bebd4"
author:
  - "[[Jonathan Chevalier]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*P8nBpSVmmJFhyTYu.png)

> OpenTelemetry is rapidly emerging as the industry standard for observability. It provides a consistent format for instrumenting and exporting application telemetry such as metrics, logs, and traces to open source or commercial observability back-ends through a standardized protocol.

Driven by a thriving open-source community, it has rapidly grown as one of the most [active](https://www.cncf.io/reports/opentelemetry-project-journey-report/) and significant CNCF projects.

Although [Micrometer](https://micrometer.io/) has been a very reliable and widely adopted solution, as the industry moves toward a more unified and standardized approach, it may struggle to keep up with the rapid pace of advancements and innovations. While it will likely remain a viable option for some use cases, the increasing adoption of OpenTelemetry is poised to drive the ecosystem.

A good example is [profiling](https://www.cncf.io/blog/2024/03/19/opentelemetry-announces-support-for-profiling/). But again, the two serve different purposes, so it is not entirely fair to compare them, but I just want to highlight how OpenTelemetry is pushing the ecosystem forward.

With this latest news and the project’s overall maturity, I felt that it was an opportune time to migrate away from [micrometer-tracing](https://docs.micrometer.io/tracing/reference/) and [micrometer-prometheus](https://docs.micrometer.io/micrometer/reference/implementations/prometheus.html) to [opentelemetry-java-instrumentation](https://github.com/open-telemetry/opentelemetry-java-instrumentation)!

## Table of Contents

1. [Automatic vs manual instrumentation](https://medium.com/@jojoooo/#e8cc)
2. [Remove dependencies](https://medium.com/@jojoooo/#0949)
3. [Add new dependencies](https://medium.com/@jojoooo/#89e7)
4. [Remove Tracer reference and miscellaneous configs](https://medium.com/@jojoooo/#e9a7)
5. [Update application properties](https://medium.com/@jojoooo/#00cd)
6. [Create opentelemetry folder and configs](https://medium.com/@jojoooo/#83bb)
7. [Update spring-boot-maven](https://medium.com/@jojoooo/#967a)
8. [Test your configuration](https://medium.com/@jojoooo/#d319)

## 1\. Automatic vs manual instrumentation

The instrumentation comes in 3 flavors:

- [Java agent](https://opentelemetry.io/docs/languages/java/automatic/) (automatic instrumentation)
- [Manual instrumentation](https://opentelemetry.io/docs/languages/java/instrumentation/)
- [spring-boot-starter](https://opentelemetry.io/docs/languages/java/automatic/spring-boot/#opentelemetry-spring-boot-starter)

I opted for the automatic instrumentation, as it will do all the [heavy lifting](https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/docs/supported-libraries.md#libraries--frameworks) for you. If you are using a [native image](https://docs.spring.io/spring-boot/docs/current/reference/html/native-image.html), already employing a monitoring agent, or you only want the [essentials,](https://opentelemetry.io/docs/languages/java/automatic/spring-boot/#automatic-instrumentation) go for the Spring Boot Starter. Finally, If you are a control freak, go for the manual 🤓.

## 2\. Remove dependencies

Remove all micrometer and exporter references from your `pom.xml`:

```c
̶<̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶
  <̶g̶r̶o̶u̶p̶I̶d̶>̶i̶o̶.̶m̶i̶c̶r̶o̶m̶e̶t̶e̶r̶<̶/̶g̶r̶o̶u̶p̶I̶d̶>̶
  <̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶m̶i̶c̶r̶o̶m̶e̶t̶e̶r̶-̶t̶r̶a̶c̶i̶n̶g̶-̶b̶r̶i̶d̶g̶e̶-̶o̶t̶e̶l̶<̶/̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶
̶<̶/̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶

̶<̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶
  <̶g̶r̶o̶u̶p̶I̶d̶>̶n̶e̶t̶.̶t̶t̶d̶d̶y̶y̶.̶o̶b̶s̶e̶r̶v̶a̶t̶i̶o̶n̶<̶/̶g̶r̶o̶u̶p̶I̶d̶>̶
  <̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶d̶a̶t̶a̶s̶o̶u̶r̶c̶e̶-̶m̶i̶c̶r̶o̶m̶e̶t̶e̶r̶-̶s̶p̶r̶i̶n̶g̶-̶b̶o̶o̶t̶<̶/̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶
̶<̶/̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶

̶<̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶
  <̶g̶r̶o̶u̶p̶I̶d̶>̶i̶o̶.̶m̶i̶c̶r̶o̶m̶e̶t̶e̶r̶<̶/̶g̶r̶o̶u̶p̶I̶d̶>̶
  <̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶m̶i̶c̶r̶o̶m̶e̶t̶e̶r̶-̶r̶e̶g̶i̶s̶t̶r̶y̶-̶p̶r̶o̶m̶e̶t̶h̶e̶u̶s̶<̶/̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶
̶<̶/̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶

̶<̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶
  <̶g̶r̶o̶u̶p̶I̶d̶>̶i̶o̶.̶o̶p̶e̶n̶t̶e̶l̶e̶m̶e̶t̶r̶y̶<̶/̶g̶r̶o̶u̶p̶I̶d̶>̶
  <̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶o̶p̶e̶n̶t̶e̶l̶e̶m̶e̶t̶r̶y̶-̶e̶x̶p̶o̶r̶t̶e̶r̶-̶o̶t̶l̶p̶<̶/̶a̶r̶t̶i̶f̶a̶c̶t̶I̶d̶>̶
̶<̶/̶d̶e̶p̶e̶n̶d̶e̶n̶c̶y̶>̶
```

## 3\. Add new dependencies

```c
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-api</artifactId>
</dependency>
```
```c
<dependencyManagement>
    <dependency>
      <groupId>io.opentelemetry</groupId>
      <artifactId>opentelemetry-bom</artifactId>
      <version>1.36.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>
```

## 4\. Remove Tracer reference and miscellaneous configs

Replace `io.micrometer.tracing.Tracer` with `io.opentelemetry.api.trace.Span` and use `Span.current().getSpanContext().getTraceId()` and `Span.current().getSpanContext().getSpanId()`.

It makes working with the span context much easier without requiring any dependency injection! You probably have other references to the Micrometer API; this is just one example. Make sure you remove all of them.

Remove miscellaneous configs like `TaskDecorator`:

```c
@̶B̶e̶a̶n̶
̶p̶u̶b̶l̶i̶c̶ ̶T̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶ ̶s̶i̶m̶p̶l̶e̶A̶s̶y̶n̶c̶T̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶(̶)̶ ̶{̶
  f̶i̶n̶a̶l̶ ̶S̶i̶m̶p̶l̶e̶A̶s̶y̶n̶c̶T̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶ ̶t̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶ ̶=̶ ̶n̶e̶w̶ ̶S̶i̶m̶p̶l̶e̶A̶s̶y̶n̶c̶T̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶(̶)̶;̶
  t̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶.̶s̶e̶t̶T̶a̶s̶k̶D̶e̶c̶o̶r̶a̶t̶o̶r̶(̶n̶e̶w̶ ̶C̶o̶n̶t̶e̶x̶t̶P̶r̶o̶p̶a̶g̶a̶t̶i̶n̶g̶T̶a̶s̶k̶D̶e̶c̶o̶r̶a̶t̶o̶r̶(̶)̶)̶;̶
  r̶e̶t̶u̶r̶n̶ ̶t̶a̶s̶k̶E̶x̶e̶c̶u̶t̶o̶r̶;̶
̶}̶
```

or `OtlpGrpcSpanExporter`:

```c
@̶B̶e̶a̶n̶
̶p̶u̶b̶l̶i̶c̶ ̶O̶t̶l̶p̶G̶r̶p̶c̶S̶p̶a̶n̶E̶x̶p̶o̶r̶t̶e̶r̶ ̶o̶t̶l̶p̶E̶x̶p̶o̶r̶t̶e̶r̶(̶f̶i̶n̶a̶l̶ ̶O̶t̶l̶p̶P̶r̶o̶p̶e̶r̶t̶i̶e̶s̶ ̶p̶r̶o̶p̶e̶r̶t̶i̶e̶s̶)̶ ̶{̶

  f̶i̶n̶a̶l̶ ̶O̶t̶l̶p̶G̶r̶p̶c̶S̶p̶a̶n̶E̶x̶p̶o̶r̶t̶e̶r̶B̶u̶i̶l̶d̶e̶r̶ ̶b̶u̶i̶l̶d̶e̶r̶ ̶=̶
    O̶t̶l̶p̶G̶r̶p̶c̶S̶p̶a̶n̶E̶x̶p̶o̶r̶t̶e̶r̶.̶b̶u̶i̶l̶d̶e̶r̶(̶)̶
      .̶s̶e̶t̶E̶n̶d̶p̶o̶i̶n̶t̶(̶p̶r̶o̶p̶e̶r̶t̶i̶e̶s̶.̶g̶e̶t̶E̶n̶d̶p̶o̶i̶n̶t̶(̶)̶)̶
      .̶s̶e̶t̶T̶i̶m̶e̶o̶u̶t̶(̶p̶r̶o̶p̶e̶r̶t̶i̶e̶s̶.̶g̶e̶t̶T̶i̶m̶e̶o̶u̶t̶(̶)̶)̶
      .̶s̶e̶t̶C̶o̶m̶p̶r̶e̶s̶s̶i̶o̶n̶(̶S̶t̶r̶i̶n̶g̶.̶v̶a̶l̶u̶e̶O̶f̶(̶p̶r̶o̶p̶e̶r̶t̶i̶e̶s̶.̶g̶e̶t̶C̶o̶m̶p̶r̶e̶s̶s̶i̶o̶n̶(̶)̶)̶.̶t̶o̶L̶o̶w̶e̶r̶C̶a̶s̶e̶(̶)̶)̶;̶

  f̶o̶r̶ ̶(̶f̶i̶n̶a̶l̶ ̶E̶n̶t̶r̶y̶<̶S̶t̶r̶i̶n̶g̶,̶ ̶S̶t̶r̶i̶n̶g̶>̶ ̶h̶e̶a̶d̶e̶r̶ ̶:̶ ̶p̶r̶o̶p̶e̶r̶t̶i̶e̶s̶.̶g̶e̶t̶H̶e̶a̶d̶e̶r̶s̶(̶)̶.̶e̶n̶t̶r̶y̶S̶e̶t̶(̶)̶)̶ ̶{̶
    b̶u̶i̶l̶d̶e̶r̶.̶a̶d̶d̶H̶e̶a̶d̶e̶r̶(̶h̶e̶a̶d̶e̶r̶.̶g̶e̶t̶K̶e̶y̶(̶)̶,̶ ̶h̶e̶a̶d̶e̶r̶.̶g̶e̶t̶V̶a̶l̶u̶e̶(̶)̶)̶;̶
  }̶

  r̶e̶t̶u̶r̶n̶ ̶b̶u̶i̶l̶d̶e̶r̶.̶b̶u̶i̶l̶d̶(̶)̶;̶
̶}̶
```

## 5\. Update application properties

Remove monitoring properties from your `application.yaml`:

```c
m̶a̶n̶a̶g̶e̶m̶e̶n̶t̶:̶
  m̶e̶t̶r̶i̶c̶s̶:̶
    d̶i̶s̶t̶r̶i̶b̶u̶t̶i̶o̶n̶:̶
      p̶e̶r̶c̶e̶n̶t̶i̶l̶e̶s̶-̶h̶i̶s̶t̶o̶g̶r̶a̶m̶:̶
        h̶t̶t̶p̶:̶
          s̶e̶r̶v̶e̶r̶:̶
            r̶e̶q̶u̶e̶s̶t̶s̶:̶ ̶t̶r̶u̶e̶
  t̶r̶a̶c̶i̶n̶g̶:̶
    s̶a̶m̶p̶l̶i̶n̶g̶:̶
      p̶r̶o̶b̶a̶b̶i̶l̶i̶t̶y̶:̶ ̶0̶
j̶d̶b̶c̶:̶
  d̶a̶t̶a̶s̶o̶u̶r̶c̶e̶-̶p̶r̶o̶x̶y̶:̶
    e̶n̶a̶b̶l̶e̶d̶:̶ ̶t̶r̶u̶e̶
s̶e̶r̶v̶e̶r̶:̶
  t̶o̶m̶c̶a̶t̶:̶
    m̶b̶e̶a̶n̶r̶e̶g̶i̶s̶t̶r̶y̶:̶
      e̶n̶a̶b̶l̶e̶d̶:̶ ̶t̶r̶u̶e̶
```

And `prometheus` from `management.endpoints.web.exposure.include`.

And add logging correlation IDs:

```c
logging:
  pattern.correlation: "[${spring.application.name:},%X{trace_id:-},%X{span_id:-},%X{trace_flags:-}]"
```

## 6\. Create OpenTelemetry folder

In the root directory, create an `opentelemetry` folder with the following [configurations](https://opentelemetry.io/docs/languages/java/automatic/configuration/):

```c
# opentelemetry/dev.properties

otel.javaagent.enabled=true
otel.javaagent.logging=application

otel.metrics.exporter=none
otel.traces.exporter=none
otel.logs.exporter=none

otel.propagators=tracecontext, baggage

otel.exporter.otlp.protocol=grpc
otel.exporter.otlp.endpoint=http://localhost:4317

otel.instrumentation.jdbc-datasource.enabled=true

otel.instrumentation.common.enduser.enabled=true
otel.instrumentation.common.enduser.id.enabled=true
otel.instrumentation.common.enduser.role.enabled=true
otel.instrumentation.common.enduser.scope.enabled=true
```
```c
# opentelemetry/default.properties

otel.javaagent.enabled=true
otel.javaagent.logging=application

otel.metrics.exporter=otlp
otel.traces.exporter=otlp
otel.logs.exporter=none

otel.propagators=tracecontext, baggage

otel.exporter.otlp.protocol=grpc
# otel.exporter.otlp.endpoint=http://localhost:4317 # set in environment

otel.instrumentation.jdbc-datasource.enabled=true

otel.instrumentation.common.enduser.enabled=true
otel.instrumentation.common.enduser.id.enabled=true
otel.instrumentation.common.enduser.role.enabled=true
otel.instrumentation.common.enduser.scope.enabled=true

# Uncomment if you want to remove resources labels: ContainerResourceProvider, HostResourceProvider, OsResourceProvider, ProcessResourceProvider, ProcessRuntimeResourceProvider
# otel.java.disabled.resource.providers=io.opentelemetry.instrumentation.resources.ContainerResourceProvider,io.opentelemetry.instrumentation.resources.HostResourceProvider,io.opentelemetry.instrumentation.resources.OsResourceProvider,io.opentelemetry.instrumentation.resources.ProcessResourceProvider,io.opentelemetry.instrumentation.resources.ProcessRuntimeResourceProvider
```

And download the latest [opentelemetry-javaagent.jar](https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar).

By default, the java agent adds (too) many labels. If you want to optimize your telemetry storage, uncomment the last line. It’s going to remove `host.arch, host.name, os.type, os.description, process.command_args process.executable.path, process.pid, process.runtime.description, process.runtime.name, process.runtime.version`.

It should look like the following:

```c
.
├── opentelemetry
│   ├── default.properties
│   ├── dev.properties
│   └── opentelemetry-javaagent.jar
```

## 7\. Update spring-boot-maven

Add the following bindings:

```c
<plugin>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-maven-plugin</artifactId>
  <configuration>
    <image>
      <env>
        <BP_JVM_VERSION>21</BP_JVM_VERSION>
      </env>
      <createdDate>${maven.build.timestamp}</createdDate>
      <bindings>
        <binding>
          ${project.basedir}/opentelemetry:/workspace/opentelemetry
        </binding>
      </bindings>
    </image>
  </configuration>
</plugin>
```

You should be ready to go!

## 8\. Test your configuration

Build your image using [buildpack](https://docs.spring.io/spring-boot/docs/current/maven-plugin/reference/htmlsingle/#goals):

```c
mvn clean package -DskipTests spring-boot:build-image
```

Install and start [otel-desktop-viewer](https://github.com/CtrlSpice/otel-desktop-viewer).

And run your image:

```c
docker run --net host \
     -e SPRING_PROFILES_ACTIVE=dev \
     -e JAVA_TOOL_OPTIONS="-javaagent:/workspace/opentelemetry/opentelemetry-javaagent.jar" \
     -e OTEL_JAVAAGENT_CONFIGURATION_FILE=/workspace/opentelemetry/dev.properties \
     -e OTEL_TRACES_EXPORTER=otlp \
     your-image-name:0.0.1-SNAPSHOT
```

You should start receiving your traces:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*G2rrv75OvbynxXpWWuh6mA.png)

If you’re looking for a working example, feel free to clone this [repository](https://github.com/Jojoooo1/spring-boot-api)!

If you want to go deeper, and build your own observability platform, take a look at my latest article: [Create your own open-source observability platform using ArgoCD, Prometheus, AlertManager, OpenTelemetry and Tempo](https://medium.com/@jojoooo/create-your-own-open-source-observability-platform-using-argocd-prometheus-alertmanager-a17cfb74bfcf?sk=279419de3dc5d0261a50569af23e2346).

*If you have any questions or suggestions, please, feel free to reach me on* [*LinkedIn*](https://www.linkedin.com/in/jonathan-chevalier-fr/)*!*

*Disclaimer: Technology development is a dynamic and evolving field, and real-world results may vary. Users should exercise their judgment, seek expert advice, and perform independent research to ensure the reliability and accuracy of any actions taken based on this tutorial. The author and publication are not liable for any consequences arising from the use of the information contained herein.*

Obsessed with DevOps & SREing. Most of my technical work is done around IAC, Security, Infra, Observability, Reactive prog., Data intensive applications \[...\]

## More from Jonathan Chevalier

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--cdb9f02bebd4---------------------------------------)