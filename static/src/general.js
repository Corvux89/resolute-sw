export function ToastError(message) {
    $("#error-toast .toast-body").html(message);
    $("#error-toast").toast("show");
}
export function ToastSuccess(message) {
    $("#confirm-toast .toast-body").html(message);
    $("#confirm-toast").toast("show");
}
if ($("#content-edit-form").length > 0) {
    //@ts-expect-error This is pulled in from a parent and no import needed
    const easyMDE = new EasyMDE({
        element: document.getElementById('content-body'),
        autofocus: true,
        sideBySideFullscreen: false,
        autoRefresh: { delay: 300 },
        maxHeight: "80vh",
        toolbar: ["undo", "redo",
            {
                "name": "save",
                className: "fa-solid fa-floppy-disk",
                action: (editor) => {
                    const key = $("#content-submit-button").data('key');
                    const content = editor.value();
                    $.ajax({
                        url: `api/content/${key}`,
                        type: "PATCH",
                        contentType: "application/json",
                        data: JSON.stringify({ content }),
                        success: function () {
                            ToastSuccess("Content saved. Refresh to view.");
                        },
                        error: function () {
                            ToastError("Failed to update content");
                        }
                    });
                }
            },
            "|", "bold", "italic", "heading", "|", "code", "quote", "unordered-list", "ordered-list", "|", "link"]
    });
    $("#content-submit-button").on('click', function () {
        const key = $(this).data('key');
        const content = easyMDE.value();
        $.ajax({
            url: `api/content/${key}`,
            type: "PATCH",
            contentType: "application/json",
            data: JSON.stringify({ content }),
            success: function () {
                location.reload();
            },
            error: function () {
                ToastError("Failed to update content");
            }
        });
    });
}
