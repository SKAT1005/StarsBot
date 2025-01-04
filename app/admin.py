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
    pass



@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass



@admin.register(Refferal_reward)
class RewardClass(admin.ModelAdmin):
    pass