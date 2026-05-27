using System.Text.Json;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CloudBilling.Data;
using CloudBilling.Models;

namespace CloudBilling.Controllers;

[Authorize]
public class InvoicesController : Controller
{
    private readonly AppDbContext _db;

    public InvoicesController(AppDbContext db) => _db = db;

    public async Task<IActionResult> Index()
    {
        ViewBag.ActivePage = "invoices";
        var invoices = await _db.Invoices
            .Include(i => i.Client)
            .OrderByDescending(i => i.Date)
            .ToListAsync();
        return View(invoices);
    }

    public async Task<IActionResult> Create()
    {
        ViewBag.ActivePage = "invoices";
        ViewBag.Clients = await _db.Clients.ToListAsync();
        ViewBag.Products = await _db.Products.ToListAsync();
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Create(int clientId, decimal total, string itemsJson)
    {
        var invoice = new Invoice
        {
            ClientId = clientId,
            Date = DateTime.Now,
            Total = total,
            Items = new List<InvoiceItem>()
        };

        var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };
        var items = JsonSerializer.Deserialize<List<InvoiceItemDto>>(itemsJson, options);
        if (items != null)
        {
            foreach (var item in items)
            {
                var product = await _db.Products.FindAsync(item.ProductId);
                if (product != null && product.Stock >= item.Quantity)
                {
                    product.Stock -= item.Quantity;
                    invoice.Items.Add(new InvoiceItem
                    {
                        ProductId = item.ProductId,
                        Quantity = item.Quantity,
                        Price = item.Price
                    });
                }
            }
        }

        _db.Invoices.Add(invoice);
        await _db.SaveChangesAsync();
        return RedirectToAction("Index");
    }

    public async Task<IActionResult> View(int id)
    {
        var invoice = await _db.Invoices
            .Include(i => i.Client)
            .Include(i => i.Items)
            .ThenInclude(ii => ii.Product)
            .FirstOrDefaultAsync(i => i.Id == id);

        if (invoice == null) return NotFound();
        ViewBag.ActivePage = "invoices";
        return View(invoice);
    }

    [HttpPost]
    public async Task<IActionResult> Delete(int id)
    {
        var invoice = await _db.Invoices
            .Include(i => i.Items)
            .FirstOrDefaultAsync(i => i.Id == id);

        if (invoice != null)
        {
            _db.InvoiceItems.RemoveRange(invoice.Items);
            _db.Invoices.Remove(invoice);
            await _db.SaveChangesAsync();
        }
        return RedirectToAction("Index");
    }

    public class InvoiceItemDto
    {
        public int ProductId { get; set; }
        public int Quantity { get; set; }
        public decimal Price { get; set; }
    }
}
