from django.db import models
from users.models import Users,CommonAction


class Notification(models.Model):
    title=models.CharField(max_length=255,null=True,blank=True)
    sender = models.ForeignKey(Users, related_name='sent_notifications', on_delete=models.CASCADE,null=True,blank=True)
    recipient=models.ForeignKey(Users, on_delete=models.CASCADE,null=True,blank=True)
    verb = models.CharField(max_length=500,null=True,blank=True)
    message=models.CharField(max_length=1000,null=True,blank=True)
    is_read=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        
        verbose_name_plural = "Notification"
        ordering = ["-id"]
        db_table = "notification"
    
    def __str__(self) :
        return str(self.title)+' '+str(self.sender.email)



TOPICS=(
    ('None','None'),
    ('Sale','Sale'),
    ('Sale Return','Sale Return'),
    ('Stock Transfer','Stock Transfer'),
    ('Stock Adjustment','Stock Adjustment'),
    ('Purchase','Purchase'),
    ('Purchase Return','Purchase Return'),
    ('Valentines','Valentines'),
    ('Pohela Baishak','Pohela Baishak'),
    ('Eid','Eid'),
    ('Ramadan','Ramadan'),
    ('Special','Special'),
    ('Other','Other')
)

class CsutomizeMessage(CommonAction):
    topics=models.CharField(max_length=500,choices=TOPICS,default='None',null=True,blank=True)
    message=models.TextField(null=True,blank=True)


    def __str__(self):
        return str(self.topics)
