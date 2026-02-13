import { Separator } from "@/components/ui/separator";
import { Bookmark, ChevronRight, User } from "lucide-react";


const ProfileSidebar = ({ active, setActive, sidebarRef }) => {
    return (
        <aside ref={sidebarRef} className="h-fit rounded-2xl border bg-background p-3 shadow-sm" >
            <div className="px-3 pb-3 pt-2">
                <div className="text-sm font-semibold">التحكم</div>
                <div className="text-xs text-muted-foreground">إدارة حسابك وحجوزاتك</div>
            </div>

            <Separator />

            <nav className="mt-3 space-y-2">
                <button
                    onClick={() => setActive("profile")}
                    className={[
                        "flex w-full items-center justify-between rounded-xl px-3 py-3 text-right transition cursor-pointer",
                        active === "profile"
                            ? "bg-emerald-600 text-white font-semibold "
                            : "hover:bg-emerald-600/50 text-muted-foreground hover:text-white",
                    ].join(" ")}
                >
                    <span className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        الصفحة الشخصية
                    </span>
                    <ChevronRight className="h-4 w-4 opacity-60" />
                </button>

                <button
                    onClick={() => setActive("bookings")}
                    className={[
                        "flex w-full items-center justify-between rounded-xl px-3 py-3 text-right transition cursor-pointer",
                        active === "bookings"
                            ? "bg-emerald-600 text-white font-semibold "
                            : "hover:bg-emerald-600/50 text-muted-foreground hover:text-white",
                    ].join(" ")}
                >
                    <span className="flex items-center gap-2">
                        <Bookmark className="h-4 w-4" />
                        الحجوزات
                    </span>
                    <ChevronRight className="h-4 w-4 opacity-60" />
                </button>
            </nav>
        </aside>
    )
}

export default ProfileSidebar