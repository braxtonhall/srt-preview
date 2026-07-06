import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

const args = process.argv.slice(2);

if (args.length < 3) {
  console.error('Usage: node encrypt.mjs <input> <output> <password>');
  process.exit(1);
}

const [inputPath, outputPath, password] = args;

const inputFile = fs.readFileSync(inputPath);

const PBKDF2_ITERATIONS = 100_000;
const KEY_LENGTH = 32; // 256 bits for AES-256-GCM
const SALT_LENGTH = 16;
const IV_LENGTH = 12; // recommended for GCM

const encryptSalt = crypto.randomBytes(SALT_LENGTH);
const iv = crypto.randomBytes(IV_LENGTH);
const verifySalt = crypto.randomBytes(SALT_LENGTH);

const verifyHash = crypto.pbkdf2Sync(password, verifySalt, PBKDF2_ITERATIONS, KEY_LENGTH, 'sha256');

const encryptKey = crypto.pbkdf2Sync(password, encryptSalt, PBKDF2_ITERATIONS, KEY_LENGTH, 'sha256');

const cipher = crypto.createCipheriv('aes-256-gcm', encryptKey, iv);

const encrypted = Buffer.concat([cipher.update(inputFile), cipher.final()]);
const authTag = cipher.getAuthTag();

const output = Buffer.concat([encryptSalt, iv, encrypted, authTag]);

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, output);

const meta = {
  outputPath,
  verifySalt: verifySalt.toString('hex'),
  verifyHash: verifyHash.toString('hex'),
};
const metaPath = outputPath + '.meta.json';
fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2) + '\n');

console.log(`Encrypted: ${inputPath} -> ${outputPath}`);
console.log(`Metadata: ${metaPath}`);
console.log(`Original size: ${inputFile.length} bytes`);
console.log(`Encrypted size: ${output.length} bytes`);
console.log('');
console.log('Copy these values into the episode config in index.html:');
console.log(`VERIFY_SALT=${verifySalt.toString('hex')}`);
console.log(`VERIFY_HASH=${verifyHash.toString('hex')}`);
