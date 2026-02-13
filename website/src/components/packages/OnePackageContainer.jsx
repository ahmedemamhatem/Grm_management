import { GetOnePackageHook } from "@/logic";
import { useState } from "react";
import { useParams } from "react-router-dom";
import OnePackageContent from "./OnePackageContent";
import OnePackageImage from "./OnePackageImage";

function OnePackageContainer() {
    const { id } = useParams();
    const { onePackage } = GetOnePackageHook(id);
    const [activeTab, setActiveTab] = useState("details")

    return (
        <section className="py-14">
            <div className="container">
                <div className="grid gap-4 md:grid-cols-12 md:gap-6">
                    <OnePackageImage
                        image={onePackage?.space_image}
                        name={onePackage?.space_name_ar || onePackage?.space_name}
                        capacity={onePackage?.capacity}
                        location={onePackage?.location_ar || onePackage?.location}
                    />

                    <OnePackageContent
                        space={onePackage}
                        activeTab={activeTab}
                        setActiveTab={setActiveTab}
                    />
                </div>
            </div>
        </section>
    );
}

export default OnePackageContainer;
