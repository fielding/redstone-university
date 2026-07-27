/**
 * Promote each course page's opening `## ` heading to an `<h1>`.
 *
 * The markdown is authored for the book, where every chapter title is an `h2`
 * under the book's single `h1`. On the web each chapter is its own document, so
 * that first heading is the page title and shipping it as an `h2` left all 11
 * course pages with no `h1` at all.
 *
 * Only the first heading is touched, and only when the document does not
 * already have an `h1`, so a file that grows a real `h1` keeps it.
 */
export function rehypePageTitle() {
    return (tree) => {
        let firstH2 = null;

        const walk = (node) => {
            for (const child of node.children ?? []) {
                if (child.type === 'element') {
                    if (child.tagName === 'h1') return true; // already has one
                    if (child.tagName === 'h2' && !firstH2) firstH2 = child;
                    if (walk(child)) return true;
                }
            }
            return false;
        };

        if (walk(tree)) return;
        if (firstH2) firstH2.tagName = 'h1';
    };
}
