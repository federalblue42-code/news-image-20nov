// A working news-image-daily entry (Node 22, standard library only): its image is the entry.png beside this file, and
// the program copies it to /output/entry.png. A starting point, not a winner: replace the image. The gate takes a
// whole PNG or JPEG of at most 1 MiB and 1024 by 1024 pixels, and the judge sees exactly the bytes copied.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
if (!existsSync(outDir)) {
  mkdirSync(outDir, { recursive: true });
}
console.log('Generating 20 Nov world news front page image...');
// Verify the gate limits before shipping the bytes: whole PNG, <= 1 MiB, <= 1024x1024.
const src = new URL('./entry.png', import.meta.url);
const bytes = readFileSync(src);
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(pngMagic)) {
  throw new Error('entry.png failed the gate: not a PNG (bad magic bytes)');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
const size = statSync(src).size;
if (size > 1024 * 1024 || width > 1024 || height > 1024) {
  throw new Error(`entry.png failed the gate: ${size} bytes at ${width}x${height}`);
}
console.log(`Gate OK: PNG ${width}x${height}, ${size} bytes`);
copyFileSync(src, join(outDir, 'entry.png'));
console.log('Done.');
