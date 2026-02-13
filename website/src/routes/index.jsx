import { RootLayout, WithGuard } from "@/components";
import LoadingPage from "@/pages/loading";
import { lazy, Suspense } from "react";
import { createHashRouter } from "react-router-dom";

const HomePage = lazy(() => import("../pages/home/index"));
const AboutPage = lazy(() => import("../pages/about/index"));
const ContactPage = lazy(() => import("../pages/contact/index"));
const WhyChooseUsPage = lazy(() => import("../pages/about/WhyChooseUs"));
const PackagesPage = lazy(() => import("../pages/packages/index"));
const OnePackagePage = lazy(() => import("../pages/packages/OnePackagePage"));
const ClientsPage = lazy(() => import("../pages/client/index"));
const ProfilePage = lazy(() => import("../pages/profile/index"));
const LoginPage = lazy(() => import("../pages/auth/Login"));
const SignUpPage = lazy(() => import("../pages/auth/Signup"));
const PageNotFound = lazy(() => import("../pages/page-not-found/index"));

const childRoutes = [
  { index: true, element: <HomePage /> },
  { path: "/about", element: <AboutPage /> },
  { path: "/contact", element: <ContactPage /> },
  { path: "/why-grm", element: <WhyChooseUsPage /> },
  { path: "/packages", element: <PackagesPage /> },
  { path: "/packages/:space/:id", element: <OnePackagePage /> },
  { path: "/clients", element: <ClientsPage /> },
  { path: "/profile", element: <WithGuard><ProfilePage /></WithGuard> },
  { path: "/login", element: <LoginPage /> },
  { path: "/sign-up", element: <SignUpPage /> },
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
