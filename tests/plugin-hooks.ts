// Functional test for opencode/plugins/spec-to-ship.ts. Run directly, or through
// `scripts/validate-kit.py` check 17:
//
//   node --experimental-strip-types tests/plugin-hooks.ts
//
// Why this exists: the plugin must refuse a secret on the ids opencode really sends
// (`edit`, `write`, `apply_patch`) and stay quiet on the plausible wrong ones (`patch`).

import plugin from "../opencode/plugins/spec-to-ship.ts";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";

const SECRET = "const k = 'sk_live_0123456789abcdefghij';";

let pass = 0;
const failures: string[] = [];

function check(name: string, ok: boolean, detail = ""): void {
  if (ok) {
    pass++;
    console.log(`  PASS  ${name}`);
  } else {
    failures.push(name + (detail ? ` — ${detail}` : ""));
    console.log(`  FAIL  ${name}${detail ? ` — ${detail}` : ""}`);
  }
}

async function hooksFor(directory: string) {
  const mod: any = await (plugin as any)({ directory });
  const before = mod["tool.execute.before"];
  if (typeof before !== "function") throw new Error("plugin exposes no tool.execute.before hook");
  return before;
}

// Returns the error thrown by the hook, or null when it allowed the call.
async function attempt(
  before: any,
  tool: string,
  args: Record<string, unknown>,
): Promise<Error | null> {
  try {
    await before({ tool }, { args });
    return null;
  } catch (e) {
    return e as Error;
  }
}

const here = fs.mkdtempSync(path.join(os.tmpdir(), "kit-plugin-"));

try {
  const before = await hooksFor(here);

  // --- Secret refusal, across every real write id ---------------------------
  check("write refuses a secret", (await attempt(before, "write", { content: SECRET })) !== null);
  check("edit refuses a secret", (await attempt(before, "edit", { newString: SECRET })) !== null);
  check(
    "apply_patch refuses a secret on an added line",
    (await attempt(before, "apply_patch", { patchText: "+" + SECRET })) !== null,
  );
  {
    const err = await attempt(before, "write", { content: SECRET });
    check(
      "refusal explains the alternative",
      !!err && /secret store|environment/.test(err.message),
    );
  }

  // --- Wrong-but-plausible tool id: `patch` is the registry variable, not the
  // id (`Tool.define("apply_patch", ...)`), so the plugin spends no match on it.
  check(
    'the non-id "patch" is not matched (apply_patch.ts defines "apply_patch")',
    (await attempt(before, "patch", { patchText: "+" + SECRET })) === null,
  );

  // --- Removing a secret is never blocked by the secret it removes ----------
  check(
    "removing a secret is allowed",
    (await attempt(before, "edit", { oldString: SECRET, newString: "const k = env;" })) === null,
  );
  check(
    "a patch that only deletes a secret is allowed",
    (await attempt(before, "apply_patch", { patchText: "-" + SECRET })) === null,
  );

  // --- Clean writes pass -----------------------------------------------------
  check(
    "clean write allowed",
    (await attempt(before, "write", { content: "class Foo {}" })) === null,
  );
  check(
    "unrelated tool untouched",
    (await attempt(before, "read", { filePath: "lib/main.dart" })) === null,
  );

} finally {
  fs.rmSync(here, { recursive: true, force: true });
}

console.log(`\n${pass} passed, ${failures.length} failed`);
process.exit(failures.length ? 1 : 0);
