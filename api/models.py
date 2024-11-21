from django.db import models
import random
import string

# Create your models here.
def gen_ran_code(length=random.randint(6,10)):
    choose=string.ascii_uppercase + string.ascii_lowercase + ''.join(str(i) for i in range(1,10))
    while True:
        code=''.join(random.choices(choose, k=length))
        if Room.objects.filter(code=code).count()==0:
            break
    return code
class Room(models.Model):
    name=models.CharField(max_length=20,null=False,default='unseted')
    code = models.CharField(max_length=8,default=gen_ran_code,unique=True)
    host= models.CharField(max_length=50,unique=True)
    guest_can_pause=models.BooleanField(null=False,default=False)
    votes_to_skip=models.IntegerField(null=False,default=1)
    created_at =models.DateTimeField(auto_now_add=True)
    current_song=models.CharField(max_length=50,null=True)
    def __str__(self):
        return self.name
    