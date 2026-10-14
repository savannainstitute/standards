# App name

One paragraph on what this app shows or does, for whom, and where its data comes from.

## Running it on your own computer

You need Node.js version 24. Install the app's packages once, then start it:

```text
npm ci
npm run dev
```

The second command prints an address. Open it in a browser to see the app. It reloads when you save
a file.

To make the files a web host serves:

```text
npm run build
```

The built site is written to a folder named dist, which is never committed.

## Layout

- `index.html`: the page the browser opens. It loads `src/main.ts`.
- `src/`: the app's code. `src/summary.ts` holds the calculations and touches neither the page nor
  the network, so it can be tested on its own. `src/main.ts` reads the data and puts the result on
  the page.
- `public/`: files served exactly as they are. `public/heights.csv` is a four-row sample written by
  hand for this template; replace it with your data.
- `tests/`: one test file per file under `src/`. Every expected number in a test carries a comment
  deriving it from the input.
- `tests/fixtures/`: the files the tests read. `tests/fixtures/README.md` says where each one comes
  from.
- `package.json`: the packages the app needs and the commands below. `package-lock.json` records the
  exact version of each package; npm writes it, so do not edit it by hand.
- `tsconfig.json`: TypeScript's settings.
- `HOSTING.md`: where the app is hosted and how to roll it back.
- A docs folder holds anything longer than this file.

## Tests

```text
npm test
npm run typecheck
```

The first command runs every test. The second checks that the types agree across the code without
running it.

A test that needs a GPU, a licensed program, another operating system or an outside service says
what it needs, using `tests/needs.ts`:

```ts
import { expect } from "vitest";

import { needs } from "./needs";

needs("the weather service")("reads today's forecast", async () => {
  expect(await forecastFor("plot 4")).toHaveProperty("rain_mm");
});
```

The check on a pull request leaves those tests out and prints how many it left out and why. On your
own computer `npm test` runs them all.

## Checks

Every pull request runs the organization's checks: lint, formatting, types, tests and the
organization's rules. The lint and formatting settings live in the organization's standards
repository, and this repository holds none of its own.

To run the rules and the YAML check before each commit:

```text
pip install pre-commit
pre-commit install
```

To run the lint and the formatter yourself, clone the standards repository into the folder next to
this one, install its tools once, and use the two commands from this folder:

```text
git clone https://github.com/savannainstitute/standards ../standards
npm ci --prefix ../standards/src/standards/configs
npm run lint
npm run format
```

`npm run lint` lists what to fix. `npm run format` rewrites the code files in place to the
organization's formatting.
