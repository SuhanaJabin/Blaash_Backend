const express = require('express');
const router = express.Router(); 

const { User, Account, Expense } = require('./models');

router.get('/test', (req, res) => {
    res.send('Test route is working');
});


const mongoose = require('mongoose');


router.post('/users', async (req, res) => {
    try {
        const { name, email, accounts } = req.body;
        const accountDocuments = await Account.insertMany(accounts);
        const user = new User({
            name,
            email,
            accounts: accountDocuments.map(account => account._id) 
        });

        await user.save();

        res.status(201).json({ message: 'User created successfully', user });
    } catch (error) {
        console.error('Error creating user:', error);
        res.status(500).json({ error: 'Failed to create user' });
    }
});



router.post('/users/:user_id/accounts/:account_id/expenses', async (req, res) => {
    try {
        const { user_id, account_id } = req.params;
        const { description, amount } = req.body;
        if (!mongoose.Types.ObjectId.isValid(user_id) || !mongoose.Types.ObjectId.isValid(account_id)) {
            return res.status(400).json({ error: 'Invalid user_id or account_id' });
        }

        const user = await User.findById(user_id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        const account = await Account.findById(account_id);
        if (!account) {
            return res.status(404).json({ error: 'Account not found' });
        }

        const expense = new Expense({ description, amount });
        await expense.save();

        account.expenses.push(expense);
        await account.save();

        res.status(201).json({ message: 'Expense added successfully', expense });
    } catch (error) {
        console.error('Error adding expense:', error);
        res.status(500).json({ error: 'Failed to add expense' });
    }
});


router.get('/users/:user_id/accounts/:account_id/expenses', async (req, res) => {
    try {
        const { account_id } = req.params;

        const account = await Account.findById(account_id).populate('expenses');
        res.status(200).json(account.expenses);
    } catch (error) {
        res.status(500).json({ error: 'Failed to retrieve expenses' });
    }
});

module.exports = router; 
