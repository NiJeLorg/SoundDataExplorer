from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# import for the CMS
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.wagtailimages.models import Image, AbstractImage, AbstractRendition
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index


# StS Models Below
class Beaches(models.Model):
	State = models.CharField(max_length=2)
	County = models.CharField(max_length=100)
	BeachID = models.CharField(max_length=8, unique=True)
	BeachName = models.CharField(max_length=200)
	OwnAccess = models.CharField(max_length=200)
	BeachLength = models.FloatField()
	BeachTier = models.IntegerField()
	StartLatitude = models.FloatField()
	StartLongitude = models.FloatField()
	EndLatitude = models.FloatField()
	EndLongitude = models.FloatField()

	class Meta:
		ordering = ["BeachName"]

	def __str__(self):
		return self.BeachName

class BeachWQSamples(models.Model):
	StateCode = models.CharField(max_length=2)
	BeachID = models.ForeignKey(Beaches, to_field='BeachID')
	BeachName = models.CharField(max_length=200)
	StationID = models.CharField(max_length=200)
	StationName = models.CharField(max_length=200)
	CountyName = models.CharField(max_length=200)
	Identifier = models.CharField(max_length=200)
	StartDate = models.DateField()
	StartTime = models.TimeField()
	ZoneCode = models.CharField(max_length=200)
	ActivityTypeCode = models.CharField(max_length=200)
	CharacteristicName = models.CharField(max_length=200)
	ResultValue = models.FloatField()
	ResultMeasureUnit = models.CharField(max_length=200)
	ResultComment = models.CharField(max_length=200)
	ActivityDepthValue = models.CharField(max_length=200)
	ActivityDepthUnitCode = models.CharField(max_length=200)
	SampleCollectionMethodIdentifier = models.CharField(max_length=200)	
	SampleCollectionMethodName = models.CharField(max_length=200)
	FieldGear = models.CharField(max_length=200)
	AnalysisDateTime = models.CharField(max_length=200)
	DetectionQuantitationLimit = models.CharField(max_length=200)

	def __str__(self):
		return self.BeachName

class WeatherStations(models.Model):
	Icao = models.CharField(max_length=4, blank=True, null=True)
	BeachID = models.ForeignKey(Beaches)
	Neighborhood = models.CharField(max_length=200, blank=True, null=True)
	City = models.CharField(max_length=200, blank=True, null=True)
	State = models.CharField(max_length=200, blank=True, null=True)
	Country = models.CharField(max_length=200, blank=True, null=True)
	Lat = models.CharField(max_length=50, blank=True, null=True)
	Lon = models.CharField(max_length=50, blank=True, null=True)
	DistanceKm = models.CharField(max_length=20, blank=True, null=True)
	DistanceMi = models.CharField(max_length=20, blank=True, null=True)

	def __str__(self):
		return self.Neighborhood

class WeatherData(models.Model):
	Station = models.ForeignKey(WeatherStations)
	Date = models.DateField()
	PrecipitationIn = models.CharField(max_length=10, blank=True, null=True)

	def __str__(self):
		return self.PrecipitationIn

class WeatherStationsPWS(models.Model):
	PwsId = models.CharField(max_length=20, blank=True, null=True)
	BeachID = models.ForeignKey(Beaches)
	Neighborhood = models.CharField(max_length=200, blank=True, null=True)
	City = models.CharField(max_length=200, blank=True, null=True)
	State = models.CharField(max_length=200, blank=True, null=True)
	Country = models.CharField(max_length=200, blank=True, null=True)
	Lat = models.CharField(max_length=50, blank=True, null=True)
	Lon = models.CharField(max_length=50, blank=True, null=True)
	DistanceKm = models.CharField(max_length=20, blank=True, null=True)
	DistanceMi = models.CharField(max_length=20, blank=True, null=True)

	def __str__(self):
		return self.PwsId

class WeatherDataPWS(models.Model):
	Station = models.ForeignKey(WeatherStationsPWS)
	Date = models.DateField()
	PrecipitationIn = models.CharField(max_length=10, blank=True, null=True)

	def __str__(self):
		return self.PrecipitationIn


# For weather data for the 2016 season and beyond
class WeatherDataHistoryAPI(models.Model):
	BeachID = models.ForeignKey(Beaches)
	DateTime = models.DateTimeField()
	PrecipitationIn = models.CharField(max_length=10, blank=True, null=True)

	def __str__(self):
		return self.PrecipitationIn


class MonthlyScores(models.Model):
	BeachID = models.ForeignKey(Beaches)
	MonthYear = models.DateField()
	NumberOfSamples = models.IntegerField()
	TotalPassSamples = models.IntegerField()
	TotalDryWeatherSamples = models.IntegerField()
	DryWeatherPassSamples = models.IntegerField()
	TotalWetWeatherSamples = models.IntegerField()
	WetWeatherPassSamples = models.IntegerField()

	def __str__(self):
		return self.NumberOfSamples

class AnnualScores(models.Model):
	BeachID = models.ForeignKey(Beaches)
	Year = models.DateField()
	NumberOfSamples = models.IntegerField()
	TotalPassSamples = models.IntegerField()
	TotalDryWeatherSamples = models.IntegerField()
	DryWeatherPassSamples = models.IntegerField()
	TotalWetWeatherSamples = models.IntegerField()
	WetWeatherPassSamples = models.IntegerField()
	WetWeatherPassSamples = models.IntegerField()
	MaxValueWet = models.IntegerField()
	MaxValueDry = models.IntegerField()

	def __str__(self):
		return self.NumberOfSamples


# models for the CMS below
# custom image model for Wagtail
class CustomImage(AbstractImage):
    # adding a caption field:
    caption = models.CharField(max_length=255, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        # adding the caption field name to the image form
        'caption',
    )


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter', 'focal_point_key'),
        )


# Delete the source image file when an image is deleted
@receiver(pre_delete, sender=CustomImage)
def image_delete(sender, instance, **kwargs):
    instance.file.delete(False)


# Delete the rendition image file when a rendition is deleted
@receiver(pre_delete, sender=CustomRendition)
def rendition_delete(sender, instance, **kwargs):
    instance.file.delete(False)


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full")
    ]

class WebsitePage(Page):

    # Database fields
    body = RichTextField()

    # Search index configuraiton
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['explorer.HomePage']
    subpage_types = []

class BeachStoryPage(Page):

    # Database fields
    date = models.DateField("Updated On")
    beach = models.ForeignKey(Beaches, on_delete=models.PROTECT)
    body = RichTextField()
    image = models.ForeignKey(
        CustomImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # Search index configuraiton
    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('date'),
    ]

    # Editor panels configuration
    content_panels = Page.content_panels + [
    	FieldPanel('beach'),
    	ImageChooserPanel('image'),
        FieldPanel('body', classname="full"),
    	FieldPanel('date'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ]

    # Parent page / subpage type rules
    parent_page_types = ['explorer.HomePage']
    subpage_types = []





