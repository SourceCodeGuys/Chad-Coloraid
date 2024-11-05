window.onload = function() {
    console.log("JavaScript is working!"); // Verify JavaScript is loaded

    // Color sets for the test
    var set1_color = ["#ac7773", "#ab746d", "#aa7468", "#ab7366", "#a67161", "#a5725f", "#a4715c", "#a47259", "#a27355", "#a27554", "#a37752", "#a37951", "#a47b4f", "#a37b48", "#a17e48", "#a18148", "#9e8449", "#998347", "#9c8a4c", "#9a894c", "#958a4c", "#8f8c49"];
    var set2_color = ["#8f8d49", "#8f8f56", "#8b9058", "#89925d", "#859461", "#829364", "#7e9665", "#7e9667", "#79976b", "#76956d", "#72996c", "#6b9870", "#6a9a73", "#699a77", "#609877", "#5a947c", "#5b987e", "#589681", "#599784", "#569685", "#549988", "#559689"];
    var set3_color = ["#559689", "#53968d", "#50988f", "#4a9990", "#459a94", "#499a95", "#4e9999", "#529a9f", "#5598a1", "#5597a3", "#5997a4", "#6294a5", "#6895a4", "#6893a6", "#6b93aa", "#6b8da6", "#7390ab", "#738eac", "#758eaa", "#798baa", "#7b86a4", "#8188a6"];
    var set4_color = ["#8188a6", "#858aa6", "#8988a6", "#8b89a5", "#9089a4", "#9188a2", "#9487a2", "#9788a1", "#98849d", "#9a8298", "#a08398", "#a07c91", "#a47e92", "#a87e91", "#a77c8d", "#a97989", "#ab7985", "#ad767d", "#ad7981", "#ad767b", "#aa7375", "#ad7775"];
    var color_sets = [set1_color, set2_color, set3_color, set4_color];

    // Initialize color blocks in the test
    for (var x = 0; x <= 3; x++) {
        var plates = 22;
        var set1 = [];
        for (var i = 2; i < plates; i++) {
            set1.push(i);
        }
        set1.sort(function() { return 0.5 - Math.random(); });

        var d = $('#sortable' + x);
        d.empty();

        set1.push(plates);
        set1.unshift(1);

        set1.forEach(function(e) {
            var s = (e === 1 || e === plates) ? "static" : "";
            d.append('<li class="cheat ui-state-default P' + e + ' ' + s + '" id="' + e + '" data-n="' + e + '" style="background-color:' + color_sets[x][e - 1] + '"> ' + e + '</li>');
        });
    }

    // Enable sortable functionality
    $('#sortable0, #sortable1, #sortable2, #sortable3').sortable({
        items: ':not(.static)',
        start: function() {
            $('.static', this).each(function() {
                var $this = $(this);
                $this.data('pos', $this.index());
            });
        },
        change: function() {
            var $sortable = $(this);
            var $statics = $('.static', this).detach();
            var $helper = $('<li></li>').prependTo(this);
            $statics.each(function() {
                var $this = $(this);
                var target = $this.data('pos');
                $this.insertAfter($('li', $sortable).eq(target));
            });
            $helper.remove();
        }
    });

    // Function to calculate scores and send results to the backend
    $('#checkMe').click(function() {
        console.log("Check Me button clicked!"); // Verify button click

        var score_set = [];
        var grand_total = 0;

        calculateScore($('#sortable0'));
        calculateScore($('#sortable1'));
        calculateScore($('#sortable2'));
        calculateScore($('#sortable3'));

        grand_total = score_set.reduce((acc, item) => acc + item, 0);

        var classification_scores = {
            protan: score_set.slice(18, 27).concat(score_set.slice(62, 70)).reduce((a, b) => a + b, 0),
            deutan: score_set.slice(10, 17).concat(score_set.slice(54, 62)).reduce((a, b) => a + b, 0),
            tritan: score_set.slice(0, 9).concat(score_set.slice(44, 53)).reduce((a, b) => a + b, 0)
        };

        var classification = Object.keys(classification_scores).reduce((a, b) => classification_scores[a] > classification_scores[b] ? a : b);

        var resultData = {
            total_score: grand_total,
            classification: classification,
            classification_scores: classification_scores
        };

        // Update localStorage with new values
        window.localStorage.setItem('total_error_score', resultData.total_score);
        window.localStorage.setItem('class_result', resultData.classification);
        window.localStorage.setItem('class_tritan', resultData.classification_scores.tritan);
        window.localStorage.setItem('class_protan', resultData.classification_scores.protan);
        window.localStorage.setItem('class_deutan', resultData.classification_scores.deutan);

        // Send results to the backend
        fetch('/save-results', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(resultData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location = "result"; // Redirect to the results page
            } else {
                console.error('Failed to save results:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));

        function calculateScore(element) {
            var arr = element.sortable("toArray");
            arr.unshift("1");
            arr.push("" + (arr.length + 1));

            var score = 0;
            for (var i = 0; i < arr.length; i++) {
                var a_score = 0;
                var a, b, likod, ikaw, tubang;

                if (i === 0) {
                    a = parseInt(element.find('.P' + arr[i]).data('n'), 10);
                    b = parseInt(element.find('.P' + arr[i + 1]).data('n'), 10);
                    a_score += Math.abs(a - b) - 1;
                    score += a_score;
                } else if (i < arr.length - 1) {
                    likod = parseInt(element.find('.P' + arr[i - 1]).data('n'), 10);
                    ikaw = parseInt(element.find('.P' + arr[i]).data('n'), 10);
                    tubang = parseInt(element.find('.P' + arr[i + 1]).data('n'), 10);
                    a_score += (Math.abs(likod - ikaw) + Math.abs(ikaw - tubang)) - 2;
                } else if (i === arr.length - 1) {
                    a = parseInt(element.find('.P' + arr[i]).data('n'), 10);
                    b = parseInt(element.find('.P' + arr[i - 1]).data('n'), 10);
                    a_score += Math.abs(a - b) - 1;
                    score += a_score;
                }
                score_set.push(a_score);
            }
            score -= 2; // Correct for fixed blocks
            return parseInt(score);
        }
    });
};
