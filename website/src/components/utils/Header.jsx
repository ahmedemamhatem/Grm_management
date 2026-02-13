import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import Cookies from "js-cookie";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";

import { navigationItems } from "@/assets/data";
import logo from "@/assets/images/logo.png";

import { LogoutHook } from "@/logic";
import { Menu, X } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";

const Header = () => {
  const { isLoggedIn, logoutSubmit } = LogoutHook();
  const [mobileOpen, setMobileOpen] = useState(false);

  const scope = useRef(null);
  const mobileMenuRef = useRef(null);
  const mobileLinksRef = useRef(null);

  const location = useLocation();


  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useGSAP(
    () => {
      const menu = mobileMenuRef.current;
      const links = mobileLinksRef.current?.querySelectorAll("a");

      if (!menu) return;

      gsap.killTweensOf(menu);
      if (links) gsap.killTweensOf(links);

      if (mobileOpen) {
        gsap.set(menu, { display: "block" });

        gsap.fromTo(
          menu,
          { height: 0, opacity: 0, y: -8 },
          {
            height: "auto",
            opacity: 1,
            y: 0,
            duration: 0.35,
            ease: "power2.out",
            clearProps: "height",
          }
        );

        if (links?.length) {
          gsap.fromTo(
            links,
            { opacity: 0, y: -6 },
            {
              opacity: 1,
              y: 0,
              duration: 0.25,
              ease: "power2.out",
              stagger: 0.05,
              delay: 0.05,
            }
          );
        }
      } else {
        gsap.to(menu, {
          height: 0,
          opacity: 0,
          y: -8,
          duration: 0.25,
          ease: "power2.inOut",
          onComplete: () => gsap.set(menu, { display: "none", clearProps: "all" }),
        });
      }
    },
    { dependencies: [mobileOpen], scope }
  );

  return (
    <header className="sticky top-0 z-100 bg-white/80 backdrop-blur border-b border-gray-200">
      <div ref={scope} className="container py-2">
        <div className="flex items-center justify-between gap-3">
          {/* Logo */}
          <Link to="/" className="shrink-0">
            <img src={logo} alt="grm logo" className="w-14" />
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6">
            <ul className="flex gap-6">
              {navigationItems.map((item) => (
                <li key={item.title}>
                  <NavLink
                    to={item.href}
                    className={({ isActive }) =>
                      `relative inline-block  transition-colors duration-300
                      hover:text-emerald-600
                      after:content-[''] after:absolute after:left-0 after:-bottom-full after:h-[2px]
                      after:bg-emerald-600 after:transition-all after:duration-300 after:ease-in-out
                      ${isActive ? "text-emerald-600 after:w-full" : " text-gray-800 after:w-0 hover:after:w-full"}`
                    }
                  >
                    {item.title}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>

          {/* Right Side */}
          <div className="flex items-center gap-3">
            {/* Auth (Desktop) */}
            <div className="hidden md:block">
              {isLoggedIn ? (
                <DropdownMenu>
                  <DropdownMenuTrigger>
                    <Avatar>
                      <AvatarImage
                        src={`${import.meta.env.VITE_API_URL}${Cookies.get("user_image")}`}
                      />
                      <AvatarFallback>
                        {(Cookies.get("full_name")?.[0] ?? "U").toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem>
                      {Cookies.get("system_user") == "no" ? (
                        <Link to="/profile">الملف الشخصي</Link>
                      ) : (
                        <a href="/app">لوحة التحكم</a>
                      )}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={logoutSubmit}>
                      تسجيل خروج
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : (
                <Link to="/login">
                  <Button variant="outline" size="lg" className="text-base">
                    دخول
                  </Button>
                </Link>
              )}
            </div>

            {/* Mobile Hamburger */}
            <button
              type="button"
              className="md:hidden inline-flex items-center justify-center rounded-lg border border-gray-200 p-2 hover:bg-gray-50 transition"
              aria-label="Toggle menu"
              aria-expanded={mobileOpen}
              onClick={() => setMobileOpen((v) => !v)}
            >
              {mobileOpen ? <X /> : <Menu />}
            </button>
          </div>
        </div>

        {/* Mobile Menu (GSAP) */}
        <div ref={mobileMenuRef} className="md:hidden mt-3 hidden">
          <div className="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden">
            <ul ref={mobileLinksRef} className="flex flex-col p-3">
              {navigationItems.map((item) => (
                <li key={item.title}>
                  <Link
                    to={item.href}
                    className="block rounded-xl px-3 py-3 text-gray-800 hover:bg-emerald-50 hover:text-emerald-700 transition"
                    onClick={() => setMobileOpen(false)}
                  >
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>

            <div className="border-t border-gray-200 p-3">
              {isLoggedIn ? (
                <div className="flex items-center justify-between">

                  {Cookies.get("system_user") == "no" ? (
                    <Link to="/profile" className="text-gray-800 hover:text-emerald-700 transition">الملف الشخصي</Link>
                  ) : (
                    <a href="/app" className="text-gray-800 hover:text-emerald-700 transition">
                      لوحة التحكم
                    </a>
                  )}
                  <Button variant="outline" onClick={logoutSubmit}>
                    تسجيل خروج
                  </Button>
                </div>
              ) : (
                <Link to="/login" className="block">
                  <Button variant="outline" size="lg" className="w-full text-base">
                    دخول
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
