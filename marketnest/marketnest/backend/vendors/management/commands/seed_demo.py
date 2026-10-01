import random
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from catalog.models import Category, Product
from reviews.models import Review
from roles.models import Role
from vendors.models import Vendor

User = get_user_model()
PASSWORD = "Demo@12345"

CATEGORIES = [
    ("Fashion", "fashion", "Shirt", 338),
    ("Electronics", "electronics", "Smartphone", 228),
    ("Home", "home", "Home", 95),
    ("Kitchen", "kitchen", "Coffee", 38),
    ("Beauty", "beauty", "Sparkles", 300),
    ("Sports", "sports", "Dumbbell", 172),
    ("Books", "books", "BookOpen", 24),
    ("Accessories", "accessories", "Watch", 268),
]

# owner email, shop, tagline, city, awning primary, awning secondary
VENDORS = [
    ("anarkali@marketnest.pk", "Anarkali Threads", "Lawn, kurtas and shawls stitched in Lahore.", "Lahore", "#FF5A8A", "#FFFFFF"),
    ("gadgets@marketnest.pk", "Gulberg Gadgets", "Honest electronics with a real warranty.", "Lahore", "#2C3BE6", "#FFFFFF"),
    ("karkhano@marketnest.pk", "Karkhano Homeware", "Tools and things for the house, straight from Peshawar.", "Peshawar", "#C4EA6B", "#1D1B54"),
    ("spice@marketnest.pk", "Sindh Spice House", "Masalas, teas and pantry staples from Karachi.", "Karachi", "#FFC533", "#1D1B54"),
    ("pottery@marketnest.pk", "Multan Blue Pottery", "Hand-painted ceramics from Multan workshops.", "Multan", "#1D1B54", "#FFFFFF"),
    ("margalla@marketnest.pk", "Margalla Outdoors", "Gear for trails, courts and the gym.", "Islamabad", "#12B5A6", "#FFFFFF"),
]

# vendor index -> (name, category slug, price, compare_at, stock, hue, description)
PRODUCTS = {
    0: [
        ("Embroidered Lawn Kurta", "fashion", 3450, 4200, 24, 340, "Three-piece cotton lawn with chikankari embroidery on the neckline. Breathable and light for summer."),
        ("Pashmina Shawl, Mustard", "fashion", 5900, None, 12, 44, "Soft blended pashmina in a deep mustard. Long enough to wear wrapped twice."),
        ("Block Print Dupatta", "fashion", 1850, 2300, 40, 312, "Hand block-printed cotton dupatta in indigo and rose. Each piece differs slightly."),
        ("Khaddar Winter Suit", "fashion", 4800, None, 18, 20, "Warm unstitched khaddar fabric with a printed shawl."),
        ("Handloom Cotton Scarf", "accessories", 950, None, 60, 350, "Light handloom scarf, useful on every season's evenings."),
    ],
    1: [
        ("Wireless Earbuds Pro", "electronics", 6900, 8500, 30, 228, "Bluetooth 5.3, 28 hours with the case, and a warranty you can actually claim in Lahore."),
        ("20,000 mAh Power Bank", "electronics", 4200, None, 45, 210, "Charges a phone about five times. Two USB-A ports and one USB-C."),
        ("Smart Fitness Band", "electronics", 5400, 6500, 22, 190, "Heart rate, sleep tracking and a battery that lasts nearly two weeks."),
        ("Gaming Mouse, 6 Buttons", "electronics", 3200, None, 36, 250, "Adjustable DPI up to 7200, braided cable, and a comfortable right-hand shape."),
        ("USB-C Fast Charger 65W", "electronics", 2800, 3400, 50, 270, "One charger for the laptop and the phone. GaN, so it stays small."),
    ],
    2: [
        ("Stainless Steel Tool Kit", "home", 4600, None, 15, 95, "42 pieces in a carry case: the screwdrivers and pliers a home actually needs."),
        ("Copper Water Jug", "kitchen", 2400, 2900, 28, 30, "Hammered copper jug that holds 1.5 litres. Hand-wash only."),
        ("Cast Iron Karahi, 12 inch", "kitchen", 3800, None, 20, 15, "Pre-seasoned and heavy. Holds heat for a proper bhuna."),
        ("Woven Storage Baskets, Set of 3", "home", 2200, 2700, 34, 60, "Sturdy cane baskets in three sizes for shelves and laundry."),
        ("Brass Door Handles, Pair", "home", 1600, None, 44, 48, "Solid brass handles with screws included. Fits standard interior doors."),
    ],
    3: [
        ("Karachi Biryani Masala, 6 Pack", "kitchen", 1200, None, 80, 38, "Six sachets, each enough for one kilo of rice. No added colour."),
        ("Doodh Patti Chai Blend, 500g", "kitchen", 1100, 1350, 65, 28, "A strong, dark blend built for boiling with milk."),
        ("Kashmiri Pink Tea Kit", "kitchen", 1650, None, 30, 350, "Tea leaves, baking soda and the instructions for a proper noon chai."),
        ("Sindhi Achar Sampler", "kitchen", 1450, 1700, 40, 52, "Four small jars: mango, lemon, mixed and chilli."),
        ("Saffron, 2g Tin", "kitchen", 2100, None, 16, 24, "Whole threads, deep in colour. Steep before using."),
    ],
    4: [
        ("Blue Pottery Serving Bowl", "home", 3400, 3900, 14, 215, "Hand-painted in cobalt and turquoise. Food safe."),
        ("Ceramic Tea Set, 6 Cups", "kitchen", 5200, None, 9, 200, "Six cups and a pot with a hand-painted floral pattern."),
        ("Decorative Wall Plate", "home", 2600, None, 25, 190, "A glazed plate made to be hung on a wall."),
        ("Hand-Painted Flower Vase", "home", 2950, 3400, 18, 225, "Tall vase in classic Multani style."),
        ("Ceramic Coaster Set", "accessories", 1300, None, 48, 205, "Set of four coasters with a cork back so they don't slip."),
    ],
    5: [
        ("Trail Running Shoes", "sports", 7800, 9200, 20, 172, "Grippy sole and a light upper for hill trails."),
        ("Yoga Mat, 6mm", "sports", 2400, None, 42, 152, "Non-slip on both sides and easy to roll up."),
        ("Adjustable Dumbbell Pair", "sports", 6800, None, 11, 180, "Each weighs 2 to 12 kg. Change the weight in seconds."),
        ("40L Hiking Backpack", "sports", 5900, 7000, 17, 165, "Rain cover included and a padded back panel for long days."),
        ("Insulated Steel Bottle, 1L", "sports", 1900, None, 70, 190, "Cold for 24 hours or hot for 12."),
    ],
}

COMMENTS = [
    "Exactly as described and arrived well packed.",
    "Good quality for the price. Would buy again.",
    "Delivery was quick. The stall even sent a message when it shipped.",
    "Better than I expected. Colours match the photos.",
    "It works well, though the packaging could be better.",
    "Bought this as a gift and it was appreciated.",
    "Solid product. Ordering a second one for my brother.",
    "Fine, but a little smaller than I pictured.",
]


class Command(BaseCommand):
    help = "Create demo roles, users, stalls, categories, products and reviews."

    def handle(self, *args, **opts):
        random.seed(7)
        roles = {n: Role.get(n) for n, _ in Role.ROLE_CHOICES}

        admin, created = User.objects.get_or_create(
            email="admin@marketnest.pk",
            defaults=dict(first_name="Market", last_name="Admin", is_staff=True, is_superuser=True, is_verified=True, role=roles["admin"]),
        )
        if created:
            admin.set_password(PASSWORD); admin.save()

        customers = []
        for i, (first, last) in enumerate([("Ayesha", "Khan"), ("Bilal", "Ahmed"), ("Sana", "Malik"), ("Hamza", "Ali"), ("Zainab", "Raza")]):
            u, c = User.objects.get_or_create(
                email=f"customer{i + 1}@marketnest.pk",
                defaults=dict(first_name=first, last_name=last, phone="0300123456%d" % i, is_verified=True, role=roles["customer"]),
            )
            if c:
                u.set_password(PASSWORD); u.save()
            customers.append(u)

        cats = {}
        for pos, (name, slug, icon, hue) in enumerate(CATEGORIES):
            cats[slug], _ = Category.objects.update_or_create(slug=slug, defaults=dict(name=name, icon=icon, hue=hue, position=pos))

        vendors = []
        for email, shop, tagline, city, a1, a2 in VENDORS:
            owner, c = User.objects.get_or_create(
                email=email, defaults=dict(first_name=shop.split()[0], last_name="Owner", is_verified=True, role=roles["vendor"]))
            if c:
                owner.set_password(PASSWORD); owner.save()
            v, _ = Vendor.objects.update_or_create(owner=owner, defaults=dict(
                shop_name=shop, tagline=tagline, city=city, awning_primary=a1, awning_secondary=a2,
                description=f"{shop} is a family-run stall in {city}. {tagline}", is_approved=True))
            vendors.append(v)

        n_products = 0
        for idx, items in PRODUCTS.items():
            for name, cat, price, compare, stock, hue, desc in items:
                from django.utils.text import slugify
                image_url = f"https://picsum.photos/seed/{slugify(name)}/900/900"
                p, created = Product.objects.get_or_create(
                    vendor=vendors[idx], name=name,
                    defaults=dict(category=cats[cat], price=Decimal(price), compare_at_price=Decimal(compare) if compare else None,
                                  stock=stock, hue=hue, description=desc, sold_count=random.randint(3, 140), image_url=image_url))
                if created:
                    n_products += 1
                    for u in random.sample(customers, random.randint(0, 4)):
                        Review.objects.create(product=p, user=u, rating=random.choice([3, 4, 4, 5, 5, 5]), comment=random.choice(COMMENTS))
                elif not p.image_url:
                    p.image_url = image_url
                    p.save(update_fields=["image_url"])

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(vendors)} stalls, {n_products} new products.\n"
            f"Logins (password {PASSWORD}):\n"
            f"  admin     admin@marketnest.pk\n  customer  customer1@marketnest.pk\n  vendor    anarkali@marketnest.pk (and gadgets@, karkhano@, spice@, pottery@, margalla@)"))
