/**
 * Dental Clinic Management System - Patient Portal Invoice Detail Controller
 * Generates screen and printable QR codes with invoice verification metadata.
 */

window.initPortalInvoiceDetail = function (config) {
    const clinicName = config.clinicName || '';
    const issueDateISO = config.issueDateISO || '';
    const totalAmount = config.totalAmount || '';
    const invoiceNum = config.invoiceNum || '';
    const currencySymbol = config.currencySymbol || '';

    const qrValue = `Clinic: ${clinicName}\nInvoice: ${invoiceNum}\nDate: ${issueDateISO}\nTotal: ${totalAmount} ${currencySymbol}`;

    if (typeof QRious !== 'undefined') {
        // Render screen QR
        const canvasScreen = document.getElementById("invoice-qrcode");
        if (canvasScreen) {
            new QRious({
                element: canvasScreen,
                value: qrValue,
                size: 150
            });
        }

        // Render print QR
        const canvasPrint = document.getElementById("print-invoice-qrcode");
        if (canvasPrint) {
            new QRious({
                element: canvasPrint,
                value: qrValue,
                size: 150
            });
        }
    }
};
