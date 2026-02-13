import DOMPurify from "dompurify";

export default function FormatHtmlContent({ htmlFromServer, className }) {
    const clean = DOMPurify.sanitize(htmlFromServer, {
        ALLOWED_ATTR: ["class"],
    });

    return <p className={className} dangerouslySetInnerHTML={{ __html: clean }} />;
}