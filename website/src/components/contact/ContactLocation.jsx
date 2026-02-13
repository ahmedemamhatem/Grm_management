import { Map, MapCircle, MapTileLayer } from "@/components/ui/map"

export default function ContactLocation() {
    const location = [24.7136, 46.6753]


    return (
        <Map center={location}>
            <MapTileLayer />
            <MapCircle center={location} radius={200} />
        </Map>
    )
}