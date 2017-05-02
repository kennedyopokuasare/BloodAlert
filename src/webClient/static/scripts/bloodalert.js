bloodTypes = []
DEFUALT_DATA_TYPE = "json"

function loadBloodTypes(event) {
    return $.ajax({
        url: "/bloodalert/bloodtypes",
        dataType: DEFUALT_DATA_TYPE
    }).done(function (data, textStatus, jqXHR) {
        bloodTypes = data.items;
        if (data.items.length > 0) {
            $dropdown = $("#bloodTypeId");
            $dropdown.append(
                $('<option></option>').val("").html("Select Blood Type")
            );
            $.each(data.items, function (index, item) {
                $dropdown.append(
                    $('<option></option>').val(item.bloodTypeId).html(item.name)
                );
            });
        }
        console.log(data)
    });
}

function handleLoginDonorButton(event) {
    var $form = $(this).closest("form");
    console.log("submit")
    $data = serializeFormTemplate($form)
    console.log($data)
}

function handleDonorRegistration(event) {
    var $form = $(this).closest("form");
    console.log("submit")
    $data = serializeFormTemplate($form)
}

function serializeFormTemplate($form) {
    var envelope = {};
    // get all the inputs into an array.
    var $inputs = $form.find(".form-group .form-control");
    $inputs.each(function () {
        envelope[this.id] = $(this).val();
    });

    var subforms = $form.find(".form_content .subform");
    subforms.each(function () {

        var data = {}

        $(this).children("input").each(function () {
            data[this.id] = $(this).val();
        });

        envelope[this.id] = data
    });
    return envelope;
}

$(function () {

    $("#loginDonorButton").click(handleLoginDonorButton);
    $("#donorRegisterbtn").click(handleDonorRegistration);

    loadBloodTypes();

});
