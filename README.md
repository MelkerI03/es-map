# es-map

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Status: Active Development](https://img.shields.io/badge/status-active-brightgreen.svg)](STATUS)

`es-map` is a command-line tool designed to generate network topology maps from the information stored in an Elasticsearch instance. Developed as part of a bachelor's thesis in computer engineering, it allows engineers to visualize predicted network structures based on Elasticsearch data.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contribution Guidelines](#contribution-guidelines)
- [Acknowledgments](#acknowledgments)

---

## Features

- Generate a static, hierarchical image of a network topology inferred from an Elasticsearch instance.
- The system accepts Elasticsearch-compatible documents (via elasticdump-style JSON exports).
These documents are treated as raw event payloads and can optionally be compiled into a columnar Parquet representation for analytical workloads.
- Currently supports visualization of subnet structures using CIDR notation.

> **Note:** This is a work in progress and actively under development.

---

## Installation

### Linux

1. Install [Nix](https://nixos.org/download.html).
2. Use one of the following commands:
   ```bash
   nix build     # Build the project
   nix run       # Run the project directly
   ```

### Windows

1.  Download the latest executable from the Releases page.

## Usage

1. Ensure you can authenticate to your Elasticsearch instance using either flags or environment variables:

| **Environment variable** | **Flag**      |
|--------------------------|---------------|
| ES_HOST                  | --host        |
| ES_PORT                  | --port        |
| ES_USERNAME              | --username    |
| ES_PASSWORD              | --password    |
| ES_API_KEY               | --api-key     |
| ES_SSL                   | --ssl         |
| ES_CA_CERT               | --ca-cert     |
| ES_CLIENT_CERT           | --client-cert |
| ES_CLIENT_KEY            | --client-key  |

> For more information, please read the [elasticsearch api documentation](https://www.elastic.co/docs/api/doc/elasticsearch/authentication).

2. Run the tool:

```bash
$ es-map [FLAGS] <SUBNETS>
```

or further information on how the tool is run:

```bash
 $ es-map --help
```

## Contribution Guidelines

Because this is a bachelors thesis, contributions must be made via forking this repository.
