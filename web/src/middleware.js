// Dev only: Astro's /_image endpoint sends Cache-Control: max-age=1yr, so the
// browser caches optimized figures forever and shows stale versions when an
// image is replaced (same URL). Force no-store in dev so replaced renders/
// diagrams always refetch. Production is untouched (real caching is wanted).
export function onRequest(context, next) {
  return next().then((response) => {
    if (import.meta.env.DEV) {
      response.headers.set('Cache-Control', 'no-store, must-revalidate');
    }
    return response;
  });
}
