from django.contrib import admin

# Import models to be modifiable in CRUD
from dssodjango.models import SSOAuthInfo

admin.site.register(SSOAuthInfo)
#admin.site.register(Ad)
#admin.site.register(Publisher)
#admin.site.register(Country)


if False:
    class PartnerAdmin(admin.ModelAdmin):
        list_per_page = 1000

        list_display = ('id', 'seconds_covered',
                        'data_unixtimestamp',
                        'partner', 'publisher', 'country', 'ad',
                        'impressions_total', 'impressions_monetized',
                        'revenue')
        ordering = ('data_unixtimestamp', 'seconds_covered',
                    'partner', 'publisher', 'country', 'ad')

        search_fields = ('data_unixtimestamp',
                         'partner__name',
                         'publisher__name',
                         'country__name',
                         'ad__name'
                         )

#admin.site.register(Partner, PartnerAdmin)
#admin.site.register(PartnerData)
