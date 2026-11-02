export const SOURCE_ROOT = "https://github.com/frankxai/awesome-motion-design-agent-skills";
export const SOURCE_REF = process.env.NEXT_PUBLIC_SOURCE_REVISION || "main";

export function sourceFile(file: string) {
  return `${SOURCE_ROOT}/blob/${SOURCE_REF}/examples/motion-lab/${file}`;
}
