namespace CloudBilling.Models;

public class Invoice
{
    public int Id { get; set; }
    public int ClientId { get; set; }
    public Client Client { get; set; } = null!;
    public DateTime Date { get; set; }
    public decimal Total { get; set; }
    public ICollection<InvoiceItem> Items { get; set; } = new List<InvoiceItem>();
}
