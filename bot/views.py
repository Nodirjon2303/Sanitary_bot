from django.shortcuts import render
from .models import *
from .Button import *
import math

state_user_name = 1
state_user_main = 2
state_user_contact = 4
state_user_savatcha = 5
state_user_muddat = 6


def start(update, context):
    user_id = update.effective_user.id
    profile, bol = Profile.objects.get_or_create(user_id=user_id)
    if bol:
        profile.first_name = update.effective_user.first_name
        profile.save()
        update.message.reply_html(f"Assalomu alaykum <b>{update.effective_user.first_name}</b>\n"
                                  f"Botimizga xush kelibsiz! \nBotdan to'liq foydalanish uchun Ism familyangizni to'liq yozib yuboring:")
        return state_user_name
    else:
        update.message.reply_html("Botimizga xush kelibsiz.\n"
                                  "Quyidagi buyruqlardan birini tanlang👇👇", reply_markup=main_button())
        return state_user_main


def command_user_name(update, context):
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_html("Telefon raqamingizni yuboring👇👇", reply_markup=phone_button())
    return state_user_contact


def command_user_contact(update, context):
    contact = update.effective_message.contact
    phone_number = contact.phone_number
    profile = Profile.objects.get(user_id=update.effective_user.id)
    profile.first_name = update.effective_user.first_name
    profile.username = update.effective_user.username
    profile.full_name = context.user_data['name']
    profile.phone = phone_number
    profile.save()
    update.message.reply_text("Siz muaffaqiyatli ro'yxatdan  o'tdingiz.\n"
                              "Botdan to'liq foydalanishingiz mumkin", reply_markup=main_button())
    return state_user_main


def command_user_addorder(update, context):
    categories = Category.objects.all()
    maxpage = context.user_data['maxpage'] = math.ceil(len(categories) / 10)
    if maxpage == 0:
        context.bot.answer_callback_query(text="Hozircha categoriyalar qo'shilmagan", callback_query_id=query.id,
                                          show_alert=True)
        return state_user_main
    context.user_data['page'] = 1
    xabar = f"{context.user_data['page']}-sahifa\n" \
            f"Categoriyalardan birini tanlang"
    update.message.reply_html(xabar, reply_markup=category_all_button(context.user_data['page']))

    return state_user_main


def command_user_savatcha(update, context):
    profile = Profile.objects.get(user_id=update.effective_user.id)
    xabar = 'Savatcha\n'
    savatcha = Savatcha.objects.filter(status='progress', profile=profile)
    sanoq = 1

    if len(savatcha) > 0:
        for i in savatcha:
            Jami = 0
            discount = 100 - ((100 - i.product.discount) * (100 - profile.discout) / 100)

            xabar += f"{sanoq}.<b>{i.product.name}</b>\n {i.quantity} x {i.product.price} = {i.quantity * i.product.price}        <b>chegirma:</b> {discount}%\n"
            Jami += i.quantity * i.product.price * (1 - (discount / 100))
        xabar += f"\nJami: {Jami}"

        update.message.reply_html(xabar, reply_markup=savatcha_button(savatcha))
        return state_user_savatcha
    else:
        update.message.reply_html("Hozircha savatcha bo'sh Savatchaga mahsulot qo'shmagansiz")
    return state_user_main


def command_user_orderhistory(update, context):
    profile = Profile.objects.get(user_id=update.effective_user.id)
    update.message.reply_html("Order history", reply_markup=ReplyKeyboardRemove())
    update.message.reply_html("Qaysi muddatdagi savdolar tarixini ko'rmoqchisiz👇👇", reply_markup=muddat_button())
    return state_user_muddat


def command_user_muddat(update, context):
    profile = Profile.objects.get(user_id=update.effective_user.id)
    query = update.callback_query
    A = query.data
    query.message.delete()
    if A == 'day':
        savatcha = Savatcha.objects.filter(profile=profile, status='done', sold_date=datetime.date.today())
        txt = 'Kunlik savdo'
        if len(savatcha):
            for i in savatcha:
                xabar = f"Mahsulot nomi: <b>{i.product.name}</b>\n" \
                        f"narxi: <b>{i.sold_price}</b>\n" \
                        f"soni: <b>{i.quantity}</b>\n" \
                        f"chegirma: <b>{i.sold_discout}</b>\n" \
                        f"Jami: <b>{i.sold_price * (1 - (i.sold_discout / 100)) * i.quantity}</b>\n" \
                        f"Sanasi: <b>{i.sold_date}</b>"
                try:
                    print(i.product.imageURL[1:])
                    query.message.reply_photo(photo=open(f"{i.product.imageURL[1:]}", 'rb'), caption=xabar,
                                              parse_mode="HTML")
                except:
                    query.message.reply_html(xabar)
            query.message.reply_html("Yuqorida Kunlik savdo keltirilgan tanishib chiqishingiz mumkin",
                                     reply_markup=main_button())
        else:
            query.message.reply_html("Belgilangan muddat bo'yicha savdolar mavjud emas", reply_markup=main_button())
    elif A == 'week':
        savatcha = Savatcha.objects.filter(profile=profile, status='done')
        dat = datetime.date.today() - datetime.timedelta(days=7)
        sanoq = 0
        for i in savatcha:
            if i.sold_date > dat:
                sanoq += 1
                xabar = f"Mahsulot nomi: <b>{i.product.name}</b>\n" \
                        f"narxi: <b>{i.sold_price}</b>\n" \
                        f"soni: <b>{i.quantity}</b>\n" \
                        f"chegirma: <b>{i.sold_discout}</b>\n" \
                        f"Jami: <b>{i.sold_price * (1 - (i.sold_discout / 100)) * i.quantity}</b>\n" \
                        f"Sanasi: <b>{i.sold_date}</b>"
                try:
                    query.message.reply_photo(photo=open(f"{i.product.imageURL}", 'rb'), caption=xabar,
                                              parse_mode="HTML")
                except:
                    query.message.reply_html(xabar)
        if sanoq == 0:
            query.message.reply_html("Ushbu muddat bo'yicha malumot yo'q", reply_markup=main_button())
        else:
            query.message.reply_html("Yuqorida Haftalik savdo keltirilgan tanishib chiqishingiz mumkin",
                                     reply_markup=main_button())
    elif A == 'month':
        savatcha = Savatcha.objects.filter(profile=profile, status='done')
        dat = datetime.date.today() - datetime.timedelta(days=30)
        sanoq = 0
        for i in savatcha:
            if i.sold_date > dat:
                sanoq += 1
                xabar = f"Mahsulot nomi: <b>{i.product.name}</b>\n" \
                        f"narxi: <b>{i.sold_price}</b>\n" \
                        f"soni: <b>{i.quantity}</b>\n" \
                        f"chegirma: <b>{i.sold_discout}</b>\n" \
                        f"Jami: <b>{i.sold_price * (1 - (i.sold_discout / 100)) * i.quantity}</b>\n" \
                        f"Sanasi: <b>{i.sold_date}</b>"
                try:
                    query.message.reply_photo(photo=open(f"{i.product.imageURL}", 'rb'), caption=xabar,
                                              parse_mode="HTML")
                except:
                    query.message.reply_html(xabar)
        if sanoq == 0:
            query.message.reply_html("Belgilangan muddat bo'yicha malumot mavjud emas", reply_markup=main_button())
        else:
            query.message.reply_html("Yuqorida oylik savdo keltirilgan tanishib chiqishingiz mumkin",
                                     reply_markup=main_button())
    elif A == 'year':
        savatcha = Savatcha.objects.filter(profile=profile, status='done', sold_date=datetime.date.today())
        dat = datetime.date.today() - datetime.timedelta(days=365)
        sanoq = 0
        for i in savatcha:
            if i.sold_date > dat:
                sanoq += 1
                xabar = f"Mahsulot nomi: <b>{i.product.name}</b>\n" \
                        f"narxi: <b>{i.sold_price}</b>\n" \
                        f"soni: <b>{i.quantity}</b>\n" \
                        f"chegirma: <b>{i.sold_discout}</b>\n" \
                        f"Jami: <b>{i.sold_price * (1 - (i.sold_discout / 100)) * i.quantity}</b>\n" \
                        f"Sanasi: <b>{i.sold_date}</b>"
                try:
                    query.message.reply_photo(photo=open(f"{i.product.imageURL}", 'rb'), caption=xabar,
                                              parse_mode="HTML")
                except:
                    query.message.reply_html(xabar)
        if sanoq == 0:
            query.message.reply_html("Belgilangan muddat bo'yicha malumot mavjud emas", reply_markup=main_button())
        else:
            query.message.reply_html("Yuqorida Yillik savdo keltirilgan tanishib chiqishingiz mumkin",
                                     reply_markup=main_button())
    else:
        query.message.reply_html("<b>main menu</b>", reply_markup=main_button())
    return state_user_main


def command_hisobkitob(update, context):
    profile = Profile.objects.get(user_id=update.effective_user.id)
    savatcha = Savatcha.objects.filter(profile=profile, status='done')
    Jami = 0
    for i in savatcha:
        Jami += i.sold_price * (1 - (i.sold_discout / 100)) * i.quantity
    update.message.reply_html(f"Jami qilgan savdoyingiz: {Jami}")
    return state_user_main


def command_info(update, context):
    profile = Profile.objects.get(user_id=update.effective_user.id)
    company = Company.objects.all()[0]
    xabar = f"Kompaniya nomi: <b>{company.company_name}</b>\n" \
            f"Manzili: <b>{company.Adress}</b>\n" \
            f"Direktor Ismi: <b>{company.director_name}</b>\n" \
            f"Masul shaxs ismi: <b>{profile.full_name}</b>\n" \
            f"Masul shaxs tel raqami: <b>{profile.phone}</b>"
    try:
        update.message.reply_photo(photo=open(f"{company.imageURL}", 'rb'), caption=xabar, parse_mode='HTML')
    except:
        update.message.reply_html(xabar)
    return state_user_main


def command_user_product(update, context):
    query = update.callback_query

    A = query.data
    if A == 'next':
        category = Category.objects.get(id=context.user_data['category'])
        print(context.user_data)
        products = Product.objects.filter(quantity__gte=1, category=category)
        context.user_data['maxpage'] = math.ceil(len(products) / 10)
        page = context.user_data['page']
        if context.user_data['maxpage'] == page:
            context.bot.answer_callback_query(callback_query_id=query.id, text="Siz oxirgi sahifaga yetib keldingiz")
        else:
            context.user_data['page'] += 1
            query.edit_message_text(text=f"{context.user_data['page']}- sahifa\n" + "Mahsulotlardan birini tanlang",
                                    reply_markup=product_all_button(context.user_data['page'],
                                                                    context.user_data['category']),
                                    parse_mode='HTML')
        return state_user_main
    elif A == 'back':
        page = context.user_data['page']
        print(context.user_data)
        if page == 1:
            context.bot.answer_callback_query(callback_query_id=query.id, text="Siz birinchi sahifaga yetib keldingiz")
        else:
            context.user_data['page'] -= 1
            print(context.user_data)
            query.edit_message_text(text=f"{page}- sahifa\n" + "Mahsulotlardan birini tanlang",
                                    reply_markup=product_all_button((page - 1), context.user_data['category']))

    elif A == 'nextc':
        categories = Category.objects.all()
        context.user_data['maxpage'] = math.ceil(len(categories) / 10)
        page = context.user_data['page']
        if context.user_data['maxpage'] == page:
            context.bot.answer_callback_query(callback_query_id=query.id, text="Siz oxirgi sahifaga yetib keldingiz")
        else:
            context.user_data['page'] += 1
            query.edit_message_text(text=f"{context.user_data['page']}- sahifa\n" + "Sahifalardan birini tanlang",
                                    reply_markup=category_all_button(context.user_data['page']),
                                    parse_mode='HTML')
        return state_user_main
    elif A == 'backc':
        page = context.user_data['page']
        print(context.user_data)
        if page == 1:
            context.bot.answer_callback_query(callback_query_id=query.id, text="Siz birinchi sahifaga yetib keldingiz")
        else:
            context.user_data['page'] -= 1
            query.edit_message_text(text=f"{page}- sahifa\n" + "Mahsulotlardan birini tanlang",
                                    reply_markup=category_all_button(page - 1))

        return state_user_main
    elif A == 'cancel':
        query.message.delete()
        query.message.reply_html("main menu")
        return state_user_main
    elif A == 'up':
        soni = context.user_data['soni']
        product = Product.objects.get(id=context.user_data['product'])
        if soni < product.quantity:
            context.user_data['soni'] += 1
            xabar = f"Nomi:{product.name}\n" \
                    f"soni: {soni + 1} ta" \
                    f"Narxi:{product.price * (soni + 1)}"
            query.edit_message_text(text=xabar, reply_markup=count_button(product.id))
        else:
            context.bot.answer_callback_query(callback_query_id=query.id,
                                              text="Siz bundan ko'p mahsulot buyutma qila olmaysiz")
    elif A == 'down':
        soni = context.user_data['soni']
        product = Product.objects.get(id=context.user_data['product'])
        if soni > 1:
            context.user_data['soni'] -= 1
            xabar = f"Nomi:{product.name}\n" \
                    f"soni: {soni - 1} ta" \
                    f"Narxi:{product.price * (soni - 1)}"
            query.edit_message_text(text=xabar, reply_markup=count_button(product.id))
        else:
            context.bot.answer_callback_query(callback_query_id=query.id,
                                              text="Siz bundan ko'p mahsulot buyutma qila olmaysiz")
    else:
        profile = Profile.objects.get(user_id=update.effective_user.id)
        try:
            data, id = A.split("_")
        except:
            a = A.split("_")
            data = a[0]
            id = a[1]
        if data == 'product':
            id = int(id)
            product = Product.objects.get(id=id)
            print(product.name, product.quantity, product.price, product.discount)
            try:
                query.message.reply_html(photo=open(f'{product.imageURL}', 'rb'),
                                         caption=f"Nomi:{product.name}\nmiqdori: {product.quantity}\nNarxi: {product.price}\nChegirma:{100 - ((100 - int(product.discount)) * (100 - int(profile.discout)) / 100)}%",
                                         reply_markup=order_button(id))
                query.message.delete()
            except:
                query.edit_message_text(text=f"Nomi:{product.name}\n"
                                             f"miqdori: {product.quantity}\n"
                                             f"Narxi: {product.price}\n"
                                             f"Chegirma:{100 - ((100 - int(product.discount)) * (100 - int(profile.discout)) / 100)}%",
                                        reply_markup=order_button(id))

        elif data == 'order':
            id = int(id)
            context.user_data['soni'] = 1
            product = Product.objects.get(id=id)
            xabar = f"Nomi:{product.name}\n" \
                    f"soni: 1 ta" \
                    f"Narxi:{product.price}"

            context.user_data['product'] = product.id
            query.edit_message_text(text=xabar, reply_markup=count_button(product.id))
        elif data == 'confirm':
            id = int(id)
            product = Product.objects.get(id=id)
            profile = Profile.objects.get(user_id=update.effective_user.id)
            soni = context.user_data['soni']
            discount = 100 - ((100 - product.discount) * (100 - profile.discout) / 100)
            savatcha = Savatcha.objects.create(profile=profile, product=product, quantity=soni, status='done',
                                               sold_discout=discount)
            savatcha.set_defaults
            savatcha.save()
            product.quantity -= soni
            product.save()
            context.bot.answer_callback_query(callback_query_id=query.id,
                                              text="Buyurtmangiz muaffaqiyatli qabul qilindi", show_alert=True)
            query.message.delete()
        elif data == 'savat':
            id = int(id)
            product = Product.objects.get(id=id)
            profile = Profile.objects.get(user_id=update.effective_user.id)
            try:
                savatcha = Savatcha.objects.get(profile=profile, product=product, status='progress')
                savatcha.quantity += 1
            except:
                savatcha = Savatcha.objects.create(profile=profile, product=product, quantity=1)
                savatcha.save()
            context.bot.answer_callback_query(text="Mahsulot savatchaga muaffaqiyatli qo'shildi",
                                              callback_query_id=query.id, show_alert=True)
            context.user_data['page'] = 1
            query.edit_message_text(text="Quyidagi categoriyalardan birini tanlang",
                                    reply_markup=category_all_button(1))
        elif data == 'category':
            id = int(id)
            context.user_data['category'] = id
            category = Category.objects.get(id=id)
            products = Product.objects.filter(category=category, quantity__gte=1)
            maxpage = context.user_data['maxpage'] = math.ceil(len(products) / 10)
            if maxpage == 0:
                context.bot.answer_callback_query(text="Hozircha mahsulotlar qo'shilmagan", callback_query_id=query.id, show_alert=True)
                return state_user_main
            context.user_data['page'] = 1
            xabar = f"{context.user_data['page']}-sahifa\n" \
                    f"Mahsulotlardan birini tanlang"
            query.edit_message_text(text=xabar, reply_markup=product_all_button(context.user_data['page'],
                                                                                context.user_data['category']))
    return state_user_main


def command_user_savatcha_conf(update, context):
    query = update.callback_query
    A = query.data
    profile = Profile.objects.get(user_id=update.effective_user.id)
    if A == 'confirm':
        savatcha = Savatcha.objects.filter(status='progress', profile=profile)
        for i in savatcha:
            i.status = 'done'
            i.set_defaults
            i.save()
        context.bot.answer_callback_query(callback_query_id=query.id, text="Buyurtmangiz muaffaqiyatli qabul qilindi",
                                          show_alert=True)
        query.message.delete()
        return state_user_main
    elif A == 'cancel':
        query.message.delete()
        query.message.reply_html("<b>main menu</b>", reply_markup=main_button())
        return state_user_main
    else:
        data, id = A.split('_')
        try:
            savatcha = Savatcha.objects.get(id=int(id))
        except:
            return state_user_savatcha
        if data == 'minus':
            if savatcha.quantity == 1:
                savatcha.delete()
            else:
                savatcha.quantity -= 1
                savatcha.save()
            xabar = 'Savatcha\n'
            savatchas = Savatcha.objects.filter(status='progress', profile=profile)
            sanoq = 1
            if len(savatchas) > 0:
                Jami = 0
                for i in savatchas:
                    discount = 100 - ((100 - i.product.discount) * (100 - profile.discout) / 100)
                    xabar += f"{sanoq}.<b>{i.product.name}</b>\n {i.quantity} x {i.product.price} = {i.quantity * i.product.price}      <b>chegirma:</b>{discount}%\n"
                    Jami += i.quantity * i.product.price * (1 - (discount / 100))
                    sanoq += 1
                xabar += f"\nJami: {Jami}"
                try:
                    query.edit_message_text(xabar, reply_markup=savatcha_button(savatchas), parse_mode='HTML')
                except:
                    return state_user_savatcha
            else:
                query.message.delete()
                query.message.reply_html("Hozircha savatcha bo'sh Savatchaga mahsulot qo'shmagansiz",
                                         reply_markup=main_button())
                return state_user_main
        elif data == 'plus':
            if savatcha.quantity < savatcha.product.quantity:
                savatcha.quantity += 1
                savatcha.save()
                xabar = 'Savatcha\n'
                savatcha = Savatcha.objects.filter(status='progress', profile=profile)
                sanoq = 1
                Jami = 0
                if len(savatcha) > 0:
                    for i in savatcha:
                        discount = 100 - ((100 - i.product.discount) * (100 - profile.discout) / 100)
                        xabar += f"{sanoq}.<b>{i.product.name}</b>\n {i.quantity} x {i.product.price} = {i.quantity * i.product.price}      <b>chegirma:</b>{discount}%\n\n"
                        sanoq += 1
                        Jami += i.quantity * i.product.price * (1 - (discount / 100))
                    xabar += f"\nJami: {Jami}"
                    query.edit_message_text(xabar, reply_markup=savatcha_button(savatcha), parse_mode='HTML')
                else:
                    query.message.delete()
                    query.edit_message_text("Hozircha savatcha bo'sh Savatchaga mahsulot qo'shmagansiz",
                                            reply_markup=main_button())
                    return state_user_main
            else:
                context.bot.answer_callback_query(callback_query_id=query.id,
                                                  text="Ushbu mahsulotdan bundan ortiqcha buyurtma qila olmaysiz")
        elif data == 'delete':
            savatcha.delete()
            xabar = 'Savatcha\n'
            savatchas = Savatcha.objects.filter(status='progress', profile=profile)
            sanoq = 1
            if len(savatchas) > 0:
                Jami = 0
                for i in savatchas:
                    discount = 100 - ((100 - i.product.discount) * (100 - profile.discout) / 100)
                    xabar += f"{sanoq}.<b>{i.product.name}</b>\n {i.quantity} x {i.product.price} = {i.quantity * i.product.price}      <b>chegirma:</b>{discount}%\n\n"
                    sanoq += 1
                    Jami += i.quantity * i.product.price * (1 - (discount / 100))
                xabar += f"\nJami: {Jami}"
                query.edit_message_text(xabar, reply_markup=savatcha_button(savatchas), parse_mode='HTML')
            else:
                query.message.delete()
                query.edit_message_text("Hozircha savatcha bo'sh Savatchaga mahsulot qo'shmagansiz",
                                        reply_markup=main_button())
                return state_user_main
        return state_user_savatcha
