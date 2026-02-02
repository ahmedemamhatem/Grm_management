
import { createRoot } from "react-dom/client";

let headRoot; 


export function SetMetaTags({
  title ,
  description,
  keywords,
  author = "GRM",
  type = "website",
}) {
    if (!headRoot) {
    headRoot = createRoot(document.head);
  }

  headRoot.render(
    <>
      {/* Basic Meta */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta name="author" content={author} />
      <meta name="viewport" content="width=device-width, initial-scale=1" />

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:site_name" content={title} />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
    </>
  );
}
