import { Toaster } from "@/components/ui/sonner"
import { Outlet, useLocation } from 'react-router-dom'
import BreadCrumb from "./BreadCrumb"
import Footer from './Footer'
import Header from './Header'

const RootLayout = () => {
  const location = useLocation();
  const exeption = ["/", "/login", "/sign-up"]
  return (
    <>
      <Header />
      {!exeption.includes(location.pathname) && <BreadCrumb />}
      <Outlet />
      <Footer />
      <Toaster />
    </>
  )
}

export default RootLayout