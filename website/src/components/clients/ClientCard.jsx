import { Button } from "../ui/button";
import { Card, CardContent } from "../ui/card";

export default function ClientCard({ image, name, description }) {
    return (
        <div className="group client-card">
            <Card
                className="
          relative overflow-hidden
          bg-white/5 border-white/10
          backdrop-blur-xl
          transition
          hover:-translate-y-1 hover:scale-[1.01]
          hover:shadow-[0_0_0_1px_rgba(5,150,105,0.25)]
        "
            >
                {/* Glow */}
                <div
                    className="
            glow pointer-events-none absolute inset-0 opacity-0
            bg-[radial-gradient(600px_circle_at_50%_0%,rgba(5,150,105,0.2),transparent_55%)]
            transition-opacity duration-200 group-hover:opacity-100
          "
                />

                <CardContent className="p-3 sm:p-4">
                    <div className="relative aspect-4/3 w-full overflow-hidden rounded-xl border border-white/10 bg-white">
                        <img
                            src={image}
                            alt={name}
                            className="h-full w-full object-contain transition-transform duration-300 group-hover:scale-[1.04]"
                            loading="lazy"
                        />
                    </div>

                    <div className="mt-3 flex items-center justify-between gap-2">
                        <div className="min-w-0">
                            <div className="text-sm sm:text-[15px] font-medium">
                                {name}
                            </div>
                            <div className="text-sm sm:text-[15px] font-medium text-gray-500">
                                {description}
                            </div>
                        </div>

                        <Button
                            size="icon"
                            variant="outline"
                            className="h-9 w-9 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10"
                            asChild
                        >
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}