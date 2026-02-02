import { Toaster } from "@/components/ui/sonner"
import { Outlet, useLocation } from 'react-router-dom'
import BreadCrumb from "./BreadCrumb"
import Footer from './Footer'
import Header from './Header'

const RootLayout = () => {
  const location = useLocation();
  return (
    <>
      <Header />
      {location.pathname !== "/" && <BreadCrumb />}
      <Outlet />
      <Footer />
      <Toaster />
    </>
  )
}

export default RootLayout