from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    path("", views.library_view, name="list"),
    path("add/", views.add_title_view, name="add"),
    path("preview/", views.media_preview_view, name="preview"),
    path("save/", views.save_title_view, name="save"),
    path("media/<int:media_id>/", views.media_detail_view, name="detail"),
    path("media/<int:media_id>/log/", views.update_library_log_view, name="update_log"),
    path("folders/", views.folder_list_view, name="folder_list"),
    path("folders/<int:folder_id>/", views.folder_detail_view, name="folder_detail"),
    path("folders/<int:folder_id>/delete/", views.folder_delete_view, name="folder_delete"),
    path("folders/<int:folder_id>/items/add/", views.folder_add_items_view, name="folder_add_items"),
    path("folders/<int:folder_id>/items/remove/", views.folder_remove_items_view, name="folder_remove_items"),
]
