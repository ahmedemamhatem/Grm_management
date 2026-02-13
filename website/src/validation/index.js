import z from "zod";

export const loginSchema = z.object({
    username: z
        .string()
        .min(1, "من فضلك اكتب اسم المستخدم"),
    password: z
        .string()
        .min(6, "كلمة المرور لازم تكون 6 حروف/أرقام على الأقل")
        .max(128, "كلمة المرور طويلة جدًا"),
})

const baseSignUpSchema = z.object({
    first_name: z.string().min(1, "من فضلك اكتب الاسم الأول").max(50, "الاسم الأول طويل جدًا"),
    last_name: z.string().min(1, "من فضلك اكتب اسم العائلة").max(50, "اسم العائلة طويل جدًا"),
    phone: z.string().min(1, "من فضلك اكتب رقم الهاتف").max(20, "رقم الهاتف طويل جدًا"),
    email: z.string().min(1, "من فضلك اكتب البريد الإلكتروني").email("من فضلك اكتب بريد إلكتروني صحيح"),
    password: z.string().min(8, "كلمة المرور لازم تكون 8 حروف/أرقام على الأقل").max(128, "كلمة المرور طويلة جدًا"),
    confirm_password: z.string().min(1, "من فضلك اكتب تأكيد كلمة المرور").max(128, "تأكيد كلمة المرور طويلة جدًا"),
});

const companySignUpSchema = baseSignUpSchema.extend({
    tenant_type: z.literal("Company"),
    company_name: z.string().min(1, "من فضلك اكتب اسم الشركة").max(120, "اسم الشركة طويل جدًا"),
    commercial_registration: z.string().min(1, "من فضلك اكتب السجل التجاري").max(30, "السجل التجاري طويل جدًا"),
    tax_id: z.string().min(1, "من فضلك اكتب الرقم الضريبي").max(30, "الرقم الضريبي طويل جدًا"),
});

const individualSignUpSchema = baseSignUpSchema.extend({
    tenant_type: z.literal("Individual"),
    company_name: z.string().optional(),
    commercial_registration: z.string().optional(),
    tax_id: z.string().optional(),
});

export const signupSchema = z
    .discriminatedUnion("tenant_type", [companySignUpSchema, individualSignUpSchema])
    .refine((data) => data.password === data.confirm_password, {
        message: "كلمة المرور غير متطابقة",
        path: ["confirm_password"],
    });

const timeRegex = /^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/

export const checkAvailabilitySpaceSchema = z
    .object({
        date: z.date({ required_error: "يجب اختيار التاريخ" }),
        start_time: z.string().regex(timeRegex, "صيغة وقت البدء غير صحيحة"),
        end_time: z.string().regex(timeRegex, "صيغة وقت الانتهاء غير صحيحة"),
    })
    .refine(
        (data) => {
            const start = data.start_time
            const end = data.end_time

            const toMinutes = (time) => {
                const [h, m] = time.split(":").map(Number)
                return h * 60 + m
            }

            return toMinutes(end) > toMinutes(start)
        },
        {
            message: "يجب اختيار وقت الانتهاء بعد وقت البدء",
            path: ["end_time"],
        }
    )

export const BookingSchema = z.object({
    attendees: z
        .number({ required_error: "عدد الحضور مطلوب" })
        .int("يجب أن يكون رقم صحيح")
        .min(1, "يجب أن يكون على الأقل 1")
        .max(500, "رقم كبير جدًا"),
    purpose: z
        .string()
        .min(2, "الغرض يجب أن يكون حرفين على الأقل")
        .max(100, "الغرض طويل جدًا"),
    notes: z
        .string()
        .max(500, "الملاحظات طويلة جدًا")
        .optional()
        .or(z.literal("")),
});

export const ChangePasswordSchema = z
    .object({
        current_password: z.string().min(1, "أدخل كلمة المرور الحالية"),
        new_password: z
            .string()
            .min(6, "كلمة المرور يجب أن تكون 6 أحرف على الأقل"),
        confirm_password: z.string(),
    })
    .refine((data) => data.new_password === data.confirm_password, {
        message: "كلمة المرور غير متطابقة",
        path: ["confirm_password"],
    })