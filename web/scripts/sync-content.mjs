import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_SRC = path.resolve(__dirname, '../../src');
const DEST_CONTENT = path.resolve(__dirname, '../src/content/course');
const DEST_ASSETS = path.resolve(__dirname, '../public/assets');

console.log('🔄 Syncing content...');

// Ensure destinations exist
if (fs.existsSync(DEST_CONTENT)) fs.rmSync(DEST_CONTENT, { recursive: true, force: true });
fs.mkdirSync(DEST_CONTENT, { recursive: true });

if (!fs.existsSync(DEST_ASSETS)) fs.mkdirSync(DEST_ASSETS, { recursive: true });

// Helper to copy directory recursively
function copyDir(src, dest) {
    if (!fs.existsSync(dest)) fs.mkdirSync(dest, { recursive: true });

    const entries = fs.readdirSync(src, { withFileTypes: true });

    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);

        if (entry.isDirectory()) {
            copyDir(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

// Copy Course Content
// We want to copy Part-*, introduction.md, etc.
const entries = fs.readdirSync(ROOT_SRC, { withFileTypes: true });
for (const entry of entries) {
    const srcPath = path.join(ROOT_SRC, entry.name);

    // Skip project_assets for content, handle separately if needed
    if (entry.name === 'project_assets') {
        // Copy to public/assets for static serving
        copyDir(srcPath, path.join(DEST_ASSETS, 'project_assets'));
        // ALSO copy to content directory because introduction.md references it relatively
        copyDir(srcPath, path.join(DEST_CONTENT, 'project_assets'));
        continue;
    }

    if (entry.isDirectory() || entry.name.endsWith('.md')) {
        const destPath = path.join(DEST_CONTENT, entry.name);
        if (entry.isDirectory()) {
            copyDir(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

console.log('✅ Content synced successfully!');

// Fix missing images
console.log('🔧 Fixing missing images...');
const placeholderPath = path.join(DEST_ASSETS, 'project_assets/logo-dark-nobg.png');

function fixMissingImages(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
            fixMissingImages(fullPath);
        } else if (entry.name.endsWith('.md')) {
            let content = fs.readFileSync(fullPath, 'utf-8');

            // Fix logo path to use dark version
            content = content.replace(/project_assets\/logo\.png/g, 'project_assets/logo-dark-nobg.png');

            const imageRegex = /!\[.*?\]\((.*?)\)/g;
            let match;
            while ((match = imageRegex.exec(content)) !== null) {
                const imagePath = match[1];
                if (imagePath.startsWith('http')) continue;

                const absoluteImagePath = path.resolve(path.dirname(fullPath), imagePath);

                if (!fs.existsSync(absoluteImagePath)) {
                    console.warn(`⚠️ Missing image: ${imagePath} in ${entry.name}. Using placeholder.`);
                    const imageDir = path.dirname(absoluteImagePath);
                    if (!fs.existsSync(imageDir)) fs.mkdirSync(imageDir, { recursive: true });
                    fs.copyFileSync(placeholderPath, absoluteImagePath);
                }
            }
            // Write back the modified content (in memory/buffer for now, but we should write it to the dest)
            fs.writeFileSync(fullPath, content);
        }
    }
}

if (fs.existsSync(placeholderPath)) {
    fixMissingImages(DEST_CONTENT);
} else {
    console.warn('⚠️ Placeholder image not found, skipping missing image fix.');
}

