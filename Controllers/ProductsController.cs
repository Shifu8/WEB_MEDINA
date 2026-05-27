using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CloudBilling.Data;
using CloudBilling.Models;

namespace CloudBilling.Controllers;

[Authorize]
public class ProductsController : Controller
{
    private readonly AppDbContext _db;

    public ProductsController(AppDbContext db) => _db = db;

    public async Task<IActionResult> Index()
    {
        ViewBag.ActivePage = "products";
        var products = await _db.Products.ToListAsync();
        return View(products);
    }

    public IActionResult Create()
    {
        ViewBag.ActivePage = "products";
        return View();
    }

    [HttpPost]
    public async Task<IActionResult> Create(Product product)
    {
        if (ModelState.IsValid)
        {
            _db.Products.Add(product);
            await _db.SaveChangesAsync();
            return RedirectToAction("Index");
        }
        ViewBag.ActivePage = "products";
        return View(product);
    }

    public async Task<IActionResult> Edit(int id)
    {
        ViewBag.ActivePage = "products";
        var product = await _db.Products.FindAsync(id);
        if (product == null) return NotFound();
        return View(product);
    }

    [HttpPost]
    public async Task<IActionResult> Edit(Product product)
    {
        if (ModelState.IsValid)
        {
            _db.Products.Update(product);
            await _db.SaveChangesAsync();
            return RedirectToAction("Index");
        }
        ViewBag.ActivePage = "products";
        return View(product);
    }

    [HttpPost]
    public async Task<IActionResult> Delete(int id)
    {
        var product = await _db.Products.FindAsync(id);
        if (product != null)
        {
            _db.Products.Remove(product);
            await _db.SaveChangesAsync();
        }
        return RedirectToAction("Index");
    }

    [HttpGet]
    public async Task<IActionResult> GetProduct(int id)
    {
        var product = await _db.Products.FindAsync(id);
        if (product == null) return NotFound();
        return Json(new { id = product.Id, name = product.Name, price = product.Price, stock = product.Stock });
    }
}
