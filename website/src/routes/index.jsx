import { RootLayout } from "@/components";
import LoadingPage from "@/pages/loading";
import { lazy, Suspense } from "react";
import { createHashRouter } from "react-router-dom";

const HomePage = lazy(() => import("../pages/home/index"));
const AboutPage = lazy(() => import("../pages/about/index"));
const PageNotFound = lazy(() => import("../pages/page-not-found/index"));

const childRoutes = [
  { index: true, element: <HomePage /> },
  { path: "/about", element: <AboutPage /> },
  { path: "*", element: <PageNotFound /> },
];

const router = createHashRouter([
  {
    path: "/",
    element: (
      <Suspense fallback={<LoadingPage />}>
        <RootLayout />
      </Suspense>
    ),
    children: childRoutes.map((route) => ({
      ...route,
      element: <Suspense fallback={<LoadingPage />}>{route.element}</Suspense>,
    })),
  },
]);


export default router;
