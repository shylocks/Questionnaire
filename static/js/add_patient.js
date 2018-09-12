$("#subBtn").on("click", function () {

    $.ajax(
        {
            url: "/add_patient/",
            type: "POST",

            data: {
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val(),
                name: $("#name").val(),
                sex: $("#sex").val(),
                age: $("#age").val(),
                idcard: $("#idcard").val(),
                nation: $("#nation").val(),
                native_place: $("#native_place").val(),
                education: $("#education").val(),
                marriage: $("#marriage").val(),
                children: $("#children").val(),
                longest_job: $("#longest_job").val(),
                family_medical_history: $("#family_medical_history").val(),
            },
            success: function (data) {
            }
        }
    )
});