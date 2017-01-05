var copyButtons = new Clipboard('[data-clipboard-target]');
function showTooltip(element, msg) {
    var $el = $(element);
    $el.tooltip({
        position: "bottom",
        container: "body",
        title: msg,
        trigger: "manual"
    }).tooltip("show");
    setTimeout(function clearTooltip() {
        $el.tooltip('destroy');
    }, 500);
}
function fallbackMessage(action) {
    var actionMsg = '';
    var actionKey = (action === 'cut' ? 'X' : 'C');
    if (/iPhone|iPad/i.test(navigator.userAgent)) {
        actionMsg = 'Copy as text';
    } else if (/Mac/i.test(navigator.userAgent)) {
        actionMsg = 'Press ⌘-' + actionKey + ' to ' + action;
    } else {
        actionMsg = 'Press Ctrl-' + actionKey + ' to ' + action;
    }
    return actionMsg;
}

copyButtons.on('success', function(e) {
    e.clearSelection();
    showTooltip(e.trigger, 'Copied!');
});
copyButtons.on('error', function(e) {
    showTooltip(e.trigger, fallbackMessage(e.action));
});