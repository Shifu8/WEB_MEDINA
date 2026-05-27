using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CloudBilling.Data;

namespace CloudBilling.Controllers;

[Authorize]
public class DashboardController : Controller
{
    private readonly AppDbContext _db;

    public DashboardController(AppDbContext db) => _db = db;

    public async Task<IActionResult> Index()
    {
        ViewBag.TotalProducts = await _db.Products.CountAsync();
        ViewBag.TotalClients = await _db.Clients.CountAsync();
        ViewBag.TotalInvoices = await _db.Invoices.CountAsync();
        var invoicesList = await _db.Invoices.ToListAsync();
        ViewBag.TotalRevenue = invoicesList.Sum(i => i.Total);
        ViewBag.ActivePage = "dashboard";
        return View();
    }
}
