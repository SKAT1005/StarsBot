from django.contrib import admin
from .models import User, UserTask, Task, Refferal_reward, Promocode, DayReward


@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    pass


@admin.register(DayReward)
class DayRewardAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ['is_admin']
    search_fields = ('username',)
    filter_horizontal = ('referral', 'tasks')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "referral":
            # Получаем ID пользователя, которого редактируем
            user_id = request.resolver_match.kwargs.get('object_id')
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    # Фильтруем список пользователей, чтобы показать только тех,
                    # кто относится к текущему пользователю (является его рефералом)
                    kwargs["queryset"] = User.objects.filter(pk__in=user.referral.all())
                except User.DoesNotExist:
                    # Если пользователь не найден, показываем пустой QuerySet
                    kwargs["queryset"] = User.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)



@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass



@admin.register(Refferal_reward)
class RewardClass(admin.ModelAdmin):
    pass