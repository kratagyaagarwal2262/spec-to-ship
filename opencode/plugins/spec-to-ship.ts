import type { Plugin } from "@opencode-ai/plugin";

/**
 * spec-to-ship hooks for opencode.
 *
 * Source of truth: this file. `scripts/kit.py install --for opencode` links it into
 * `~/.config/opencode/plugins/`; never hand-edit the installed copy.
 *
 * Parity with the kit's command hook (`hooks/spec-to-ship-hook.py`):
 * - `secrets` (UserPromptSubmit) -> below, moved to the file-write boundary: opencode has no
 *   prompt-submit hook, so `edit` / `write` / `apply_patch` calls whose *new* content looks like
 *   an API key, token, or JWT are refused with an error. The ids are literal
 *   (`Tool.define("apply_patch", ...)` in `apply_patch.ts`; the tools doc says to check
 *   `apply_patch`, not `patch`). This keeps a secret out of source at the point it would enter.
 *
 * Everything else fails open.
 */

// Same shapes as SECRET_RE in hooks/spec-to-ship-hook.py: Stripe keys, AWS access keys,
// GitHub PATs, JWTs, and bearer tokens.
const SECRET_RE =
  /sk_(live|test)_[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9_\-.=]{20,}/;

// What the tool call is about to write. For `edit`, only the *new* text is
// checked, so removing a secret is never blocked by the secret it removes.
// For `apply_patch`, only added (`+`) lines are checked for the same reason.
function newContent(args: Record<string, unknown>): string {
  const texts: string[] = [];
  for (const key of ["content", "text", "newString", "newText", "input"]) {
    const v = args[key];
    if (typeof v === "string") texts.push(v);
  }
  const patch = args["patchText"];
  if (typeof patch === "string") {
    texts.push(
      patch
        .split("\n")
        .filter((line) => line.startsWith("+") && !line.startsWith("+++"))
        .join("\n"),
    );
  }
  const diff = args["patch"];
  if (typeof diff === "string") texts.push(diff);
  if (texts.length > 0) return texts.join("\n");
  // Unknown shape: fall back to the whole args blob, minus the old text an
  // edit is replacing, so a removal cannot trip the check.
  const rest: Record<string, unknown> = { ...args };
  delete rest["oldString"];
  delete rest["oldText"];
  try {
    return JSON.stringify(rest);
  } catch {
    return "";
  }
}

export default (async () => {
  return {
    "tool.execute.before": async (input: any, output: any) => {
      const tool = input?.tool as string | undefined;
      const args = (output?.args ?? {}) as Record<string, unknown>;
      if (tool === "edit" || tool === "write" || tool === "apply_patch") {
        if (SECRET_RE.test(newContent(args))) {
          throw new Error(
            "Refusing to write a likely secret (API key / token / JWT). " +
              "Keep secrets out of source and load them from the environment or a secret store.",
          );
        }
      }
    },
  };
}) satisfies Plugin;
