using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CloudBilling.Data;
using CloudBilling.Models;

namespace CloudBilling.Controllers;

[Authorize]
public class ClientsController : Controller
{
    private readonly AppDbContext _db;

    public ClientsController(AppDbContext db) => _db = db;

    public async Task<IActionResult> Index()
    {
        ViewBag.ActivePage = "clients";
        var clients = await _db.Clients.ToListAsync();
        return View(clients);
    }

    public IActionResult Create()
    {
        ViewBag.ActivePage = "clients";
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Create(Client client)
    {
        if (ModelState.IsValid)
        {
            _db.Clients.Add(client);
            await _db.SaveChangesAsync();
            return RedirectToAction("Index");
        }
        ViewBag.ActivePage = "clients";
        return View(client);
    }

    public async Task<IActionResult> Edit(int id)
    {
        ViewBag.ActivePage = "clients";
        var client = await _db.Clients.FindAsync(id);
        if (client == null) return NotFound();
        return View(client);
    }

    [HttpPost]
    public async Task<IActionResult> Edit(Client client)
    {
        if (ModelState.IsValid)
        {
            _db.Clients.Update(client);
            await _db.SaveChangesAsync();
            return RedirectToAction("Index");
        }
        ViewBag.ActivePage = "clients";
        return View(client);
    }

    [HttpPost]
    public async Task<IActionResult> Delete(int id)
    {
        var client = await _db.Clients.FindAsync(id);
        if (client != null)
        {
            _db.Clients.Remove(client);
            await _db.SaveChangesAsync();
        }
        return RedirectToAction("Index");
    }
}
