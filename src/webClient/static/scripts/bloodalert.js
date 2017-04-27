function handleLoginDonorButton(event){
    var $form = $(this).closest("form");
    console.log("submit mit")
    $data=serializeFormTemplate($form)
    console.log($data)
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

});
