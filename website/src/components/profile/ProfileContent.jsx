import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { GetProfileHook, UpdateProfileHook } from "@/logic";
import { AtSign, Calendar, Edit3, Image as ImageIcon, Mail, Phone, User, Users } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { ProfileSkeleton } from "..";
import ProfileChangePassword from "./ProfileChangePassword";

const ProfileContent = ({ cardRef, fieldsRef }) => {
    const fileInputRef = useRef(null);
    const { profile, isLoading } = GetProfileHook();
    const { updateProfileFN, profileUpdate, isLoading: updateLoading } = UpdateProfileHook();
    const [isEditing, setIsEditing] = useState(false);
    const [avatarFile, setAvatarFile] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState(`${import.meta.env.VITE_API_URL}${profile?.user_image}`);


    const [form, setForm] = useState(() => ({
        firstName: profile?.first_name ?? "",
        lastName: profile?.last_name ?? "",
        email: profile?.email ?? "",
        username: profile?.username ?? "",
        birthDate: profile?.date_of_birth ?? "",
        gender: profile?.gender ?? "",
        avatarUrl: profile?.user_image ?? "",
        phone: profile?.phone ?? "",
    }));

    // sync when user changes from outside
    useEffect(() => {
        setForm({
            firstName: profile?.first_name ?? "",
            lastName: profile?.last_name ?? "",
            email: profile?.email ?? "",
            username: profile?.username ?? "",
            birthDate: profile?.date_of_birth ?? "",
            gender: profile?.gender ?? "",
            avatarUrl: profile?.user_image ?? "",
            phone: profile?.phone ?? "",
        });

        setAvatarPreview(`${import.meta.env.VITE_API_URL}${profile?.user_image}`);
        setAvatarFile(null);
    }, [profile]);

    const handleChange = (key, val) => {
        setForm((prev) => ({ ...prev, [key]: val }));
    };

    const startEditing = () => setIsEditing(true);

    const handleCancel = () => {
        // cleanup preview URL if it was created
        if (avatarFile && avatarPreview?.startsWith("blob:")) {
            URL.revokeObjectURL(avatarPreview);
        }

        setForm({
            firstName: profile?.first_name ?? "",
            lastName: profile?.last_name ?? "",
            email: profile?.email ?? "",
            username: profile?.username ?? "",
            birthDate: profile?.date_of_birth ?? "",
            gender: profile?.gender ?? "",
            avatarUrl: profile?.user_image ?? "",
            phone: profile?.phone ?? "",
        });

        setAvatarPreview(`${import.meta.env.VITE_API_URL}${profile?.user_image}`);
        setAvatarFile(null);
        setIsEditing(false);
    };

    const handleConfirm = () => {
        const payload = {
            firstName: form.firstName,
            lastName: form.lastName,
            birthDate: form.birthDate,
            gender: form.gender,
            avatarUrl: form.avatarUrl,
            avatarFile: avatarFile || null,
            phone: form.phone,
        };

        updateProfileFN({ first_name: payload.firstName, last_name: payload.lastName, phone: payload.phone });
        setIsEditing(false);
    };

    useEffect(() => {
        if (!updateLoading && Object.keys(profileUpdate).length > 0)
            toast.success("تم تحديث الملف الشخصي")
    }, [profileUpdate, updateLoading]);

    const handleAvatarClick = () => {
        if (!isEditing) return;
        fileInputRef.current?.click();
    };

    const handleAvatarChange = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (file.size > 2 * 1024 * 1024) return;

        if (avatarPreview?.startsWith("blob:")) {
            URL.revokeObjectURL(avatarPreview);
        }

        setAvatarFile(file);
        setAvatarPreview(URL.createObjectURL(file));
    };

    const initials = `${(profile?.first_name?.[0] || "").toUpperCase()}${(profile?.last_name?.[0] || "").toUpperCase()}`;

    if (isLoading) {
        return <ProfileSkeleton />
    }

    return (
        <Card ref={cardRef} className="rounded-2xl shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                    {/* Avatar  */}
                    <div
                        className={`relative ${isEditing ? "cursor-pointer" : ""}`}
                        onClick={handleAvatarClick}
                        role={isEditing ? "button" : undefined}
                        tabIndex={isEditing ? 0 : -1}
                        onKeyDown={(e) => {
                            if (!isEditing) return;
                            if (e.key === "Enter" || e.key === " ") handleAvatarClick();
                        }}
                        aria-label={isEditing ? "تغيير الصورة" : "صورة المستخدم"}
                    >
                        <Avatar className="h-14 w-14">
                            <AvatarImage className="object-cover" src={avatarPreview} alt={`${form.firstName} ${form.lastName}`} />
                            <AvatarFallback>{initials || "U"}</AvatarFallback>
                        </Avatar>

                        {isEditing && (
                            <div className="absolute inset-0 grid place-items-center rounded-full bg-black/50">
                                <div className="flex items-center gap-1 text-xs text-white">
                                    <ImageIcon className="h-3.5 w-3.5" />
                                    تغيير
                                </div>
                            </div>
                        )}

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={handleAvatarChange}
                        />
                    </div>

                    <div className="min-w-0">
                        <CardTitle className="truncate text-xl">
                            {form.firstName} {form.lastName}
                        </CardTitle>
                        <CardDescription className="flex items-center gap-0.5">
                            <span className="truncate">{form.username}</span>
                            <AtSign className="h-4 w-4" />
                        </CardDescription>
                    </div>
                </div>

                {/* Edit button */}
                <Button
                    variant="outline"
                    onClick={startEditing}
                    disabled={isEditing}
                    className="gap-2"
                >
                    <Edit3 className="h-4 w-4" />
                    تعديل
                </Button>
            </CardHeader>

            <CardContent>
                <div ref={fieldsRef} className="grid grid-cols-1 gap-3 md:grid-cols-2">
                    <FieldRow
                        icon={User}
                        label="الاسم الأول"
                        name="firstName"
                        value={form.firstName}
                        editable={isEditing}
                        onChange={handleChange}
                    />
                    <FieldRow
                        icon={Users}
                        label="الاسم الثاني"
                        name="lastName"
                        value={form.lastName}
                        editable={isEditing}
                        onChange={handleChange}
                    />

                    {/* Readonly */}
                    <FieldRow
                        icon={Mail}
                        label="الإيميل"
                        name="email"
                        value={form.email}
                        editable={isEditing}
                        disabled
                        onChange={handleChange}
                        type="email"
                    />
                    {/* Readonly */}
                    <FieldRow
                        icon={Phone}
                        label="رقم الهاتف"
                        name="phone"
                        value={form.phone}
                        editable={isEditing}
                        onChange={handleChange}
                    />

                    <FieldRow
                        icon={Calendar}
                        label="تاريخ الميلاد"
                        name="birthDate"
                        value={form.birthDate}
                        editable={isEditing}
                        disabled
                        onChange={handleChange}
                        type="date"
                    />
                    <FieldRow
                        icon={Users}
                        label="النوع"
                        name="gender"
                        value={form.gender}
                        editable={isEditing}
                        disabled
                        onChange={handleChange}
                        type="text"
                    />
                    {/* <FieldRow
                        icon={Users}
                        label="النوع"
                        name="gender"
                        value={form.gender}
                        editable={isEditing}
                        disabled
                        onChange={handleChange}
                        type="select"
                        options={[
                            { label: "ذكر", value: "male" },
                            { label: "أنثى", value: "female" },
                        ]}
                    /> */}
                </div>

                <Separator className="my-6" />

                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div className="text-sm text-muted-foreground">
                        اذا محتاج تغيير أي بيانات، اضغط <span className="font-medium text-foreground">تعديل</span>.
                        {isEditing ? (
                            <span className="ml-2">(الإيميل واسم المستخدم غير قابلين للتعديل)</span>
                        ) : null}
                    </div>

                    <div className="flex gap-2">
                        <Button variant="outline" onClick={handleCancel} disabled={!isEditing}>
                            إلغاء
                        </Button>
                        <Button onClick={handleConfirm} disabled={!isEditing || updateLoading}>
                            تأكيد
                        </Button>
                    </div>
                </div>

                <Separator className="my-6" />

                <ProfileChangePassword />
            </CardContent>
        </Card>
    );
};

export default ProfileContent;

function FieldRow({
    icon: Icon,
    label,
    value,
    name,
    editable,
    disabled,
    onChange,
    type = "text",
    options = [],
}) {
    return (
        <div className="flex items-start gap-3 rounded-xl border bg-background p-4">
            <div className="mt-0.5 rounded-lg border p-2">
                <Icon className="h-4 w-4" />
            </div>

            <div className="min-w-0 flex-1">
                <Label className="text-sm text-muted-foreground" htmlFor={name}>
                    {label}
                </Label>

                {/* EDIT MODE */}
                {editable ? (
                    type === "select" ? (
                        <Select
                            value={value || ""}
                            onValueChange={(val) => onChange?.(name, val)}
                            disabled={disabled}
                        >
                            <SelectTrigger className="mt-2 w-full">
                                <SelectValue placeholder="اختر" />
                            </SelectTrigger>

                            <SelectContent>
                                {options.map((opt) => (
                                    <SelectItem key={opt.value} value={opt.value}>
                                        {opt.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    ) : (
                        <Input
                            id={name}
                            name={name}
                            type={type}
                            className="mt-2"
                            value={value ?? ""}
                            onChange={(e) => onChange?.(name, e.target.value)}
                            disabled={disabled}
                        />
                    )
                ) : (
                    <div className="mt-2 truncate text-base font-medium">
                        {value || "—"}
                    </div>
                )}

                {editable && disabled && (
                    <div className="mt-1 text-xs text-muted-foreground">
                        غير قابل للتعديل
                    </div>
                )}
            </div>
        </div>
    );
}
